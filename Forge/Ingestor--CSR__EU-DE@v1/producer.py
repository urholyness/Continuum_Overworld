#!/usr/bin/env python3
"""
CSR Event Producer for Continuum_Overworld
Produces CSR_INGESTED events and writes to core.document
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

import psycopg2
from psycopg2.extras import RealDictCursor
from confluent_kafka import Producer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")
DB_DSN = os.getenv("PG_DSN", "postgresql://bridge_admin:bridge_secure_2025@localhost:5432/continuum")
TENANT_ID = os.getenv("TENANT_ID", "GSG")
PROJECT_TAG = os.getenv("PROJECT_TAG", "CSR-EU-DE-2025")

class CSRProducer:
    def __init__(self):
        """Initialize the CSR producer"""
        # Initialize Kafka producer
        self.producer = Producer({
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'csr-producer'
        })
        
        # Database connection
        self.db_conn = psycopg2.connect(DB_DSN, cursor_factory=RealDictCursor)
        
    def create_csr_event(self, doc_id: str, org_id: str, source_uri: str) -> Dict[str, Any]:
        """Create a CSR_INGESTED event"""
        event_id = str(uuid.uuid4())
        
        event = {
            "headers": {
                "world": "Continuum_Overworld",
                "division": "Forge",
                "capability": "Ingestor",
                "role": "CSR",
                "qualifier": "EU-DE",
                "version": "v1.0.0",
                "tenant_id": TENANT_ID,
                "project_tag": PROJECT_TAG,
                "agent_run_id": f"csr_producer_{int(time.time())}",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "payload_schema": "csr.ingested.v1",
                "correlation_id": event_id,
                "causation_id": None
            },
            "payload": {
                "doc_id": doc_id,
                "org_id": org_id,
                "org_code": "GSG_DE",
                "source_uri": source_uri,
                "hash": f"sha256_{doc_id}",
                "document_metadata": {
                    "title": f"CSR Report 2024 - {org_id}",
                    "document_type": "csr_report",
                    "reporting_year": 2024,
                    "source_uri": source_uri,
                    "hash": f"sha256_{doc_id}"
                }
            }
        }
        
        return event, event_id
    
    def write_document(self, doc_id: str, org_id: str, source_uri: str) -> bool:
        """Write document record to core.document"""
        try:
            with self.db_conn.cursor() as cur:
                # Set tenant context
                cur.execute("SELECT set_config('app.tenant_id', %s, true)", (TENANT_ID,))
                
                # Insert document
                cur.execute("""
                    INSERT INTO core.document 
                    (doc_id, tenant_id, project_tag, doc_type, title, source_uri, content_hash, processing_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (doc_id) DO NOTHING
                """, (
                    doc_id, TENANT_ID, PROJECT_TAG, 'csr_report',
                    f"CSR Report 2024 - {org_id}", source_uri, f"sha256_{doc_id}", 'pending'
                ))
                
                self.db_conn.commit()
                return True
                
        except Exception as e:
            print(f"Failed to write document: {e}")
            self.db_conn.rollback()
            return False
    
    def produce_event(self, event: Dict[str, Any], event_id: str) -> bool:
        """Produce event to Kafka"""
        try:
            # Convert event to JSON
            event_json = json.dumps(event)
            
            # Produce to Kafka
            self.producer.produce(
                topic="Continuum_Overworld.Forge_Ingestor--CSR__EU-DE@v1.events",
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
    
    def run(self):
        """Main producer loop"""
        print(f"Starting CSR Producer for tenant: {TENANT_ID}, project: {PROJECT_TAG}")
        
        # Sample documents to process
        sample_docs = [
            ("doc_csr_gsg_de_001", "org_gsg_de", "s3://lake/documents/csr_gsg_de_2024.pdf"),
            ("doc_csr_gsg_de_002", "org_gsg_de", "s3://lake/documents/csr_gsg_de_2023.pdf"),
            ("doc_csr_partner_de_001", "org_partner_de", "s3://lake/documents/csr_partner_de_2024.pdf"),
        ]
        
        for doc_id, org_id, source_uri in sample_docs:
            print(f"Processing document: {doc_id}")
            
            # Create event
            event, event_id = self.create_csr_event(doc_id, org_id, source_uri)
            
            # Write to database
            if self.write_document(doc_id, org_id, source_uri):
                print(f"✓ Document written to database: {doc_id}")
                
                # Produce event
                if self.produce_event(event, event_id):
                    print(f"✓ Event produced: {event_id}")
                else:
                    print(f"✗ Failed to produce event: {event_id}")
            else:
                print(f"✗ Failed to write document: {doc_id}")
            
            # Small delay between documents
            time.sleep(1)
        
        print("CSR Producer completed")
    
    def close(self):
        """Clean up resources"""
        self.producer.flush()
        self.producer.close()
        self.db_conn.close()

def main():
    """Main entry point"""
    producer = CSRProducer()
    try:
        producer.run()
    finally:
        producer.close()

if __name__ == "__main__":
    main()