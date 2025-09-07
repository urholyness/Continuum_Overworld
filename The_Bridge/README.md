# The_Bridge — Data & Agent Foundation

## Overview
Central control plane providing multi-tenant data core and shared agent memory for all Continuum_Overworld projects.

## Architecture

### Core Components
- **PostgreSQL + pgvector**: Multi-tenant OLTP with RLS and vector embeddings
- **Redpanda**: Event streaming (Kafka-compatible)
- **MinIO**: S3-compatible lakehouse storage
- **Neo4j**: Graph relationships
- **DataHub**: Data governance and lineage
- **Redis**: Hot cache (optional)

### Key Features
- ✅ **Row-Level Security**: Complete tenant isolation
- ✅ **Shared Memory Bank**: Vector search + KV store for agents
- ✅ **Event-Driven**: Contract-based event bus
- ✅ **Reference Data**: Shared DEFRA factors, HS codes
- ✅ **Data Lineage**: Full tracking with DataHub

## Quick Start

### 1. Start Infrastructure
```bash
cd infra
chmod +x startup.sh
./startup.sh
```

### 2. Verify Installation
```bash
python3 verify_bridge.py
```

Expected output:
```
✅ RLS Isolation: PASSED
✅ Event Round-trip: PASSED
✅ Embeddings: PASSED
✅ Agent Trace: PASSED
✅ Reference Data: PASSED
```

### 3. Connect Your Project

#### For Python Projects
```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Connect with tenant context
conn = psycopg2.connect(
    host="localhost",
    database="continuum",
    user="app_gsg",
    password="gsg_secure_2025"
)

with conn.cursor(cursor_factory=RealDictCursor) as cur:
    # CRITICAL: Set tenant context
    cur.execute("SELECT set_config('app.tenant_id', 'GSG', true)")
    
    # Now queries are tenant-isolated
    cur.execute("SELECT * FROM core.document")
    docs = cur.fetchall()  # Only GSG documents
```

#### For Node.js Projects
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  database: 'continuum',
  user: 'app_gsg',
  password: 'gsg_secure_2025'
});

async function query(text, params) {
  const client = await pool.connect();
  try {
    // CRITICAL: Set tenant context
    await client.query("SELECT set_config('app.tenant_id', 'GSG', true)");
    return await client.query(text, params);
  } finally {
    client.release();
  }
}
```

## Agent Memory Bank

### Store Embeddings
```python
# Store document with embedding
embedding = openai_client.embeddings.create(
    input=document_text,
    model="text-embedding-ada-002"
).data[0].embedding

cur.execute("""
    INSERT INTO core.memory_doc 
    (doc_id, tenant_id, scope, title, content, embedding)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (doc_id, tenant_id, 'project:ESG-2025', title, content, embedding))
```

### Vector Search
```python
# Search similar documents
cur.execute("""
    SELECT doc_id, title, content,
           1 - (embedding <=> %s::vector) as similarity
    FROM core.memory_doc
    WHERE tenant_id = %s
    ORDER BY embedding <=> %s::vector
    LIMIT 10
""", (query_embedding, tenant_id, query_embedding))
```

### KV Store
```python
# Store agent settings
cur.execute("""
    INSERT INTO core.memory_kv (key, tenant_id, scope, value)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
""", ('agent_config', tenant_id, 'agent:Orion', json.dumps(config)))
```

## Event Bus

### Publish Event
```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:19092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

event = {
    "headers": {
        "world": "Continuum_Overworld",
        "division": "Oracle",
        "capability": "Calculator",
        "version": "v1.0.0",
        "tenant_id": "GSG",
        "occurred_at": datetime.utcnow().isoformat(),
        "payload_schema": "esg.metric.v1"
    },
    "payload": {
        "doc_id": "doc_001",
        "metrics": [...]
    }
}

producer.send('continuum.events', event)
```

### Consume Events
```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'continuum.events',
    bootstrap_servers='localhost:19092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    event = message.value
    if event['headers']['tenant_id'] == 'GSG':
        process_event(event)
```

## Data Classification

| Level | Description | Examples | Handling |
|-------|------------|----------|----------|
| 🟢 Green | Public | Reference data, published metrics | No encryption required |
| 🟡 Amber | Internal | Shipments, agent traces | TLS required, audit logged |
| 🔴 Red | Confidential | Contracts, API keys | Encrypted at rest, MFA |
| ⚫ Black | Restricted | PII, payment data | AES-256, approval workflow |

## Project Integration

### Forge/Ingestor
```python
# Emit CSR ingestion event
event = {
    "headers": {...},
    "payload": {
        "doc_id": hash_document(content),
        "source_uri": "s3://lake-bronze/csr/2024/doc.pdf"
    }
}
producer.send('continuum.events', event)

# Store in core
cur.execute("""
    INSERT INTO core.document (doc_id, tenant_id, doc_type, source_uri)
    VALUES (%s, %s, 'csr_report', %s)
""", (doc_id, tenant_id, source_uri))
```

### Oracle/Calculator
```python
# Process emissions
cur.execute("""
    INSERT INTO core.emissions_event 
    (tenant_id, shipment_id, co2e_kg, calculation_method)
    VALUES (%s, %s, %s, 'ISO14083')
""", (tenant_id, shipment_id, emissions))

# Store in memory for agents
cur.execute("""
    INSERT INTO core.memory_doc (doc_id, tenant_id, scope, content, embedding)
    VALUES (%s, %s, 'project:emissions', %s, %s)
""", (f"emission_{event_id}", tenant_id, summary, embedding))
```

### Orion/MAR/MCP
```python
# Record agent run
cur.execute("""
    INSERT INTO core.agent_run 
    (agent_run_id, tenant_id, agent_name, input, status, started_at)
    VALUES (%s, %s, %s, %s, 'running', NOW())
""", (run_id, tenant_id, 'Orion_Reasoner', input_json))

# Search memory
similar_docs = cur.execute("""
    SELECT * FROM core.search_memory_docs(%s, %s, 'global', 10)
""", (query_embedding, tenant_id)).fetchall()

# Get agent context
context = cur.execute("""
    SELECT core.get_agent_context(%s, %s, 24)
""", (agent_name, tenant_id)).fetchone()
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS for all connections
- [ ] Configure firewall rules
- [ ] Set up backup strategy
- [ ] Enable audit logging
- [ ] Review RLS policies
- [ ] Implement key rotation
- [ ] Set up monitoring alerts

## Monitoring

### Health Checks
```bash
# Database
docker exec bridge_postgres pg_isready

# Kafka
docker exec bridge_redpanda rpk cluster health

# MinIO
curl http://localhost:9000/minio/health/live
```

### Metrics
- Tenant activity: `SELECT tenant_id, COUNT(*) FROM bridge.event_registry GROUP BY tenant_id`
- Agent performance: `SELECT agent_name, AVG(duration_ms) FROM core.agent_run GROUP BY agent_name`
- Memory usage: `SELECT pg_size_pretty(pg_database_size('continuum'))`

## Troubleshooting

### RLS Not Working
```sql
-- Check current tenant
SELECT current_setting('app.tenant_id', true);

-- Verify RLS enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'core';
```

### Event Processing Failed
```python
# Check event registry
cur.execute("""
    SELECT * FROM bridge.event_registry 
    WHERE status = 'failed'
    ORDER BY occurred_at DESC
""")
```

### Vector Search Slow
```sql
-- Check index
\di *embedding*

-- Rebuild if needed
REINDEX INDEX core.idx_memory_doc_embedding;
```

## Support

- **Issues**: Create in `/The_Bridge/issues/`
- **Docs**: See `/The_Bridge/docs/`
- **Owners**: The_Bridge team

---

**Version**: 0.1.0  
**Status**: Operational  
**Classification**: Amber (Internal)