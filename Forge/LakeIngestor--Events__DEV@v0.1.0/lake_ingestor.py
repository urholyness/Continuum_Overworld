#!/usr/bin/env python3
"""
Lake Ingestor for The_Bridge Event Streaming
Consumes events from Redpanda and writes partitioned Parquet to MinIO
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
import time
import signal

import pyarrow as pa
import pyarrow.parquet as pq
import s3fs
import structlog
from confluent_kafka import Consumer, KafkaException, KafkaError
from dotenv import load_dotenv

load_dotenv()

# Configuration
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:19092'),
    'group.id': os.getenv('CONSUMER_GROUP_ID', 'lake-ingestor'),
    'auto.offset.reset': os.getenv('AUTO_OFFSET_RESET', 'earliest'),
    'enable.auto.commit': True,
    'session.timeout.ms': 30000,
    'fetch.wait.max.ms': 1000
}

TOPICS = os.getenv('TOPICS', 'continuum.events,continuum.memory,continuum.metrics').split(',')
BUCKET = os.getenv('LAKE_BUCKET', 'lake')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))
FLUSH_INTERVAL = int(os.getenv('FLUSH_INTERVAL_SECONDS', '30'))

# S3/MinIO configuration
S3_ENDPOINT = os.getenv('S3_ENDPOINT', 'http://localhost:9000')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', 'bridge_admin')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', 'bridge_secure_2025')

# Setup logging
logger = structlog.get_logger("lake_ingestor")

class LakeIngestor:
    def __init__(self):
        self.s3 = s3fs.S3FileSystem(
            endpoint_url=S3_ENDPOINT,
            key=S3_ACCESS_KEY,
            secret=S3_SECRET_KEY,
            use_ssl=False
        )
        self.consumer = Consumer(KAFKA_CONFIG)
        self.buffers: Dict[tuple, List[Dict[str, Any]]] = {}
        self.last_flush = time.time()
        self.running = True
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Lake Ingestor initialized", 
                   topics=TOPICS, bucket=BUCKET, batch_size=BATCH_SIZE)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received", signal=signum)
        self.running = False
    
    def _get_partition_path(self, event: Dict[str, Any], topic: str) -> tuple:
        """Generate partition path tuple for event"""
        headers = event.get('headers', {})
        
        # Extract partition keys with fallbacks
        tenant_id = headers.get('tenant_id', 'UNKNOWN')
        project_tag = headers.get('project_tag', 'GLOBAL')
        
        # Parse occurred_at to get date
        occurred_at = headers.get('occurred_at', datetime.utcnow().isoformat())
        try:
            dt = datetime.fromisoformat(occurred_at.replace('Z', '+00:00'))
            ds = dt.date().isoformat()
        except (ValueError, AttributeError):
            ds = datetime.utcnow().date().isoformat()
        
        # Clean topic name (replace / with _)
        topic_clean = topic.replace('/', '_').replace(' ', '_')
        
        return (topic_clean, tenant_id, project_tag, ds)
    
    def _write_parquet_batch(self, partition_key: tuple, rows: List[Dict[str, Any]]):
        """Write batch of rows to Parquet file"""
        topic, tenant_id, project_tag, ds = partition_key
        
        # Generate partition path
        timestamp = int(time.time())
        path = f"{BUCKET}/bronze/topic={topic}/tenant_id={tenant_id}/project_tag={project_tag}/ds={ds}/part-{timestamp}.parquet"
        
        try:
            # Convert to PyArrow table
            table = pa.Table.from_pylist(rows)
            
            # Write to S3/MinIO with compression
            with self.s3.open(path, 'wb') as f:
                pq.write_table(table, f, compression='zstd')
            
            logger.info("Wrote parquet batch", 
                       path=path, records=len(rows), 
                       tenant=tenant_id, project=project_tag)
            
        except Exception as e:
            logger.error("Failed to write parquet batch", 
                        path=path, error=str(e), records=len(rows))
            raise
    
    def _process_message(self, msg):
        """Process a single Kafka message"""
        try:
            # Parse JSON event
            raw_event = json.loads(msg.value().decode('utf-8'))
            
            # Validate event structure
            if 'headers' not in raw_event:
                logger.warning("Event missing headers", topic=msg.topic())
                return
            
            # Get partition key
            partition_key = self._get_partition_path(raw_event, msg.topic())
            
            # Prepare record for storage
            record = {
                '_raw': json.dumps(raw_event),
                'event_id': raw_event.get('event_id', raw_event.get('headers', {}).get('agent_run_id')),
                'topic': msg.topic(),
                'partition': msg.partition(),
                'offset': msg.offset(),
                'ingested_at': datetime.utcnow().isoformat()
            }
            
            # Add to buffer
            if partition_key not in self.buffers:
                self.buffers[partition_key] = []
            
            self.buffers[partition_key].append(record)
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse message JSON", 
                        topic=msg.topic(), error=str(e))
        except Exception as e:
            logger.error("Failed to process message", 
                        topic=msg.topic(), error=str(e))
    
    def _should_flush(self) -> bool:
        """Determine if buffers should be flushed"""
        current_time = time.time()
        
        # Flush if total records exceed batch size
        total_records = sum(len(buffer) for buffer in self.buffers.values())
        if total_records >= BATCH_SIZE:
            logger.debug("Flushing due to batch size", total_records=total_records)
            return True
        
        # Flush if time interval exceeded
        if current_time - self.last_flush >= FLUSH_INTERVAL:
            logger.debug("Flushing due to time interval")
            return True
        
        return False
    
    def _flush_buffers(self):
        """Flush all buffers to storage"""
        if not self.buffers:
            return
        
        flush_count = 0
        for partition_key, records in list(self.buffers.items()):
            if records:  # Only flush non-empty buffers
                try:
                    self._write_parquet_batch(partition_key, records)
                    flush_count += len(records)
                    self.buffers.pop(partition_key)
                except Exception as e:
                    logger.error("Failed to flush buffer", 
                                partition_key=partition_key, error=str(e))
        
        if flush_count > 0:
            logger.info("Flushed buffers", records_written=flush_count, 
                       partitions_flushed=len(self.buffers))
        
        self.last_flush = time.time()
    
    def run(self):
        """Main ingestion loop"""
        logger.info("Starting lake ingestion", topics=TOPICS)
        
        self.consumer.subscribe(TOPICS)
        
        try:
            while self.running:
                # Poll for messages
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    # Check if we should flush on timeout
                    if self._should_flush():
                        self._flush_buffers()
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug("Reached end of partition", 
                                   topic=msg.topic(), partition=msg.partition())
                    else:
                        logger.error("Kafka error", error=str(msg.error()))
                    continue
                
                # Process the message
                self._process_message(msg)
                
                # Check if we should flush
                if self._should_flush():
                    self._flush_buffers()
                
        except KafkaException as e:
            logger.error("Kafka exception", error=str(e))
        except Exception as e:
            logger.error("Unexpected error", error=str(e))
        finally:
            # Flush remaining buffers
            logger.info("Shutting down, flushing remaining buffers")
            self._flush_buffers()
            
            # Close consumer
            self.consumer.close()
            logger.info("Lake ingestor stopped")

def main():
    """Entry point"""
    try:
        ingestor = LakeIngestor()
        ingestor.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error("Fatal error", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()