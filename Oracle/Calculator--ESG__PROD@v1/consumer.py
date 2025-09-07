#!/usr/bin/env python3
"""
Oracle ESG Calculator Consumer for Continuum_Overworld
Consumes CSR_INGESTED events, extracts KPIs, emits ESG_METRIC_EXTRACTED events
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

import psycopg2
from psycopg2.extras import RealDictCursor
from confluent_kafka import Consumer, Producer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")
DB_DSN = os.getenv("PG_DSN", "postgresql://bridge_admin:bridge_secure_2025@localhost:5432/continuum")
TENANT_ID = os.getenv("TENANT_ID", "GSG")
PROJECT_TAG = os.getenv("PROJECT_TAG", "ESG-CALC-2025")

class ESGCalculator:
    def __init__(self):
        """Initialize the ESG Calculator"""
        # Initialize Kafka consumer
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'esg-calculator',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })
        
        # Initialize Kafka producer
        self.producer = Producer({
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'esg-calculator-producer'
        })
        
        # Subscribe to CSR events
        self.consumer.subscribe(['Continuum_Overworld.Forge_Ingestor--CSR__EU-DE@v1.events'])
        
        # Database connection
        self.db_conn = psycopg2.connect(DB_DSN, cursor_factory=RealDictCursor)
        
    def extract_esg_metrics(self, doc_id: str, org_id: str) -> List[Dict[str, Any]]:
        """Extract ESG metrics from document (simulated)"""
        # In a real implementation, this would use LLM/ML to extract metrics
        # For now, we'll simulate extraction with sample data
        
        sample_metrics = [
            {
                "metric_type": "scope1",
                "metric_name": "Direct Emissions",
                "value": 12450.0,
                "unit": "tCO2e",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "confidence": 0.95,
                "method": "llm_extraction",
                "model_version": "gpt-4-turbo-2024",
                "page_reference": 15,
                "text_snippet": "Direct emissions from owned facilities: 12,450 tCO2e"
            },
            {
                "metric_type": "scope2",
                "metric_name": "Indirect Emissions",
                "value": 8230.0,
                "unit": "tCO2e",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "confidence": 0.92,
                "method": "llm_extraction",
                "model_version": "gpt-4-turbo-2024",
                "page_reference": 16,
                "text_snippet": "Purchased electricity and heating: 8,230 tCO2e"
            },
            {
                "metric_type": "scope3_cat4",
                "metric_name": "Upstream Transport",
                "value": 156780.0,
                "unit": "tCO2e",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "confidence": 0.88,
                "method": "llm_extraction",
                "model_version": "gpt-4-turbo-2024",
                "page_reference": 18,
                "text_snippet": "Value chain emissions including transport: 156,780 tCO2e"
            },
            {
                "metric_type": "water_consumption",
                "metric_name": "Total Water Usage",
                "value": 450000.0,
                "unit": "m3",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "confidence": 0.90,
                "method": "llm_extraction",
                "model_version": "gpt-4-turbo-2024",
                "page_reference": 22,
                "text_snippet": "Total water consumption: 450,000 m³"
            },
            {
                "metric_type": "waste_generated",
                "metric_name": "Waste Generation",
                "value": 2340.0,
                "unit": "tonnes",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "confidence": 0.87,
                "method": "llm_extraction",
                "model_version": "gpt-4-turbo-2024",
                "page_reference": 25,
                "text_snippet": "Total waste generated: 2,340 tonnes, 78% recycled"
            }
        ]
        
        return sample_metrics
    
    def write_esg_metrics(self, doc_id: str, org_id: str, metrics: List[Dict[str, Any]]) -> List[str]:
        """Write ESG metrics to core.esg_metric"""
        metric_ids = []
        
        try:
            with self.db_conn.cursor() as cur:
                # Set tenant context
                cur.execute("SELECT set_config('app.tenant_id', %s, true)", (TENANT_ID,))
                
                for metric in metrics:
                    cur.execute("""
                        INSERT INTO core.esg_metric 
                        (tenant_id, doc_id, org_id, metric_type, metric_name, value, unit,
                         period_start, period_end, confidence, method, model_version)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING metric_id
                    """, (
                        TENANT_ID, doc_id, org_id, metric['metric_type'], metric['metric_name'],
                        metric['value'], metric['unit'], metric['period_start'], metric['period_end'],
                        metric['confidence'], metric['method'], metric['model_version']
                    ))
                    
                    metric_id = cur.fetchone()['metric_id']
                    metric_ids.append(metric_id)
                
                self.db_conn.commit()
                print(f"✓ Wrote {len(metrics)} ESG metrics to database")
                
        except Exception as e:
            print(f"Failed to write ESG metrics: {e}")
            self.db_conn.rollback()
        
        return metric_ids
    
    def write_memory_docs(self, doc_id: str, metrics: List[Dict[str, Any]]) -> bool:
        """Write chunked metrics to core.memory_doc for vector search"""
        try:
            with self.db_conn.cursor() as cur:
                # Set tenant context
                cur.execute("SELECT set_config('app.tenant_id', %s, true)", (TENANT_ID,))
                
                for i, metric in enumerate(metrics):
                    # Create memory document for each metric
                    memory_doc_id = f"{doc_id}_metric_{i+1}"
                    content = f"{metric['metric_name']}: {metric['value']} {metric['unit']} ({metric['metric_type']})"
                    
                    cur.execute("""
                        INSERT INTO core.memory_doc 
                        (doc_id, tenant_id, scope, title, content, doc_type, source_uri, meta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (doc_id) DO UPDATE SET 
                            content = EXCLUDED.content,
                            meta = EXCLUDED.meta,
                            updated_at = NOW()
                    """, (
                        memory_doc_id, TENANT_ID, f"project:{PROJECT_TAG}",
                        f"ESG Metric: {metric['metric_name']}", content, 'esg_metric',
                        f"doc:{doc_id}", json.dumps(metric)
                    ))
                
                self.db_conn.commit()
                print(f"✓ Wrote {len(metrics)} memory documents")
                return True
                
        except Exception as e:
            print(f"Failed to write memory docs: {e}")
            self.db_conn.rollback()
            return False
    
    def create_esg_event(self, doc_id: str, org_id: str, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create ESG_METRIC_EXTRACTED event"""
        event_id = str(uuid.uuid4())
        
        event = {
            "headers": {
                "world": "Continuum_Overworld",
                "division": "Oracle",
                "capability": "Calculator",
                "role": "ESG",
                "qualifier": "PROD",
                "version": "v1.0.0",
                "tenant_id": TENANT_ID,
                "project_tag": PROJECT_TAG,
                "agent_run_id": f"esg_calculator_{int(time.time())}",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "payload_schema": "esg.metric.v1",
                "correlation_id": event_id,
                "causation_id": None
            },
            "payload": {
                "doc_id": doc_id,
                "org_id": org_id,
                "org_code": "GSG_DE",
                "metrics": metrics,
                "document_metadata": {
                    "title": f"ESG Metrics Extracted - {doc_id}",
                    "document_type": "csr_report",
                    "reporting_year": 2024,
                    "source_uri": f"doc:{doc_id}",
                    "hash": f"sha256_{doc_id}"
                }
            }
        }
        
        return event, event_id
    
    def produce_event(self, event: Dict[str, Any], event_id: str) -> bool:
        """Produce ESG_METRIC_EXTRACTED event to Kafka"""
        try:
            # Convert event to JSON
            event_json = json.dumps(event)
            
            # Produce to Kafka
            self.producer.produce(
                topic="Continuum_Overworld.Oracle_Calculator--ESG__PROD@v1.events",
                key=event_id.encode('utf-8'),
                value=event_json.encode('utf-8'),
                callback=self.delivery_report
            )
            
            # Flush to ensure delivery
            self.producer.flush()
            return True
            
        except Exception as e:
            print(f"Failed to produce event: {e}")
            return False
    
    def delivery_report(self, err, msg):
        """Kafka delivery report callback"""
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
    
    def process_csr_event(self, event: Dict[str, Any]) -> bool:
        """Process a CSR_INGESTED event"""
        try:
            payload = event['payload']
            doc_id = payload['doc_id']
            org_id = payload['org_id']
            
            print(f"Processing CSR event for document: {doc_id}")
            
            # Extract ESG metrics
            metrics = self.extract_esg_metrics(doc_id, org_id)
            print(f"✓ Extracted {len(metrics)} ESG metrics")
            
            # Write metrics to database
            metric_ids = self.write_esg_metrics(doc_id, org_id, metrics)
            if not metric_ids:
                return False
            
            # Write memory documents
            if not self.write_memory_docs(doc_id, metrics):
                return False
            
            # Create and produce ESG event
            esg_event, event_id = self.create_esg_event(doc_id, org_id, metrics)
            if self.produce_event(esg_event, event_id):
                print(f"✓ Produced ESG_METRIC_EXTRACTED event: {event_id}")
                return True
            else:
                print(f"✗ Failed to produce ESG event")
                return False
                
        except Exception as e:
            print(f"Failed to process CSR event: {e}")
            return False
    
    def run(self):
        """Main consumer loop"""
        print(f"Starting ESG Calculator for tenant: {TENANT_ID}, project: {PROJECT_TAG}")
        
        try:
            while True:
                # Poll for messages
                msg = self.consumer.poll(1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == 1001:  # _PARTITION_EOF
                        continue
                    else:
                        print(f"Kafka error: {msg.error()}")
                        continue
                
                try:
                    # Parse event
                    event = json.loads(msg.value().decode('utf-8'))
                    
                    # Process CSR event
                    if self.process_csr_event(event):
                        # Commit offset on success
                        self.consumer.commit(msg)
                    else:
                        print(f"Failed to process event, skipping commit")
                        
                except json.JSONDecodeError as e:
                    print(f"Failed to parse message: {e}")
                except Exception as e:
                    print(f"Unexpected error processing message: {e}")
                
        except KeyboardInterrupt:
            print("Shutting down...")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            self.consumer.close()
            self.producer.flush()
            self.producer.close()
            self.db_conn.close()
            print("ESG Calculator stopped")
    
    def close(self):
        """Clean up resources"""
        self.consumer.close()
        self.producer.flush()
        self.producer.close()
        self.db_conn.close()

def main():
    """Main entry point"""
    calculator = ESGCalculator()
    try:
        calculator.run()
    finally:
        calculator.close()

if __name__ == "__main__":
    main()