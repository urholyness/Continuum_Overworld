#!/usr/bin/env python3
"""
Memory Bank API for Continuum_Overworld
REST endpoints for vector search, KV operations, and agent context
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Header, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MemoryBank API",
    description="Shared agent memory for Continuum_Overworld",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DB_DSN = os.getenv("PG_DSN", "postgresql://bridge_admin:bridge_secure_2025@localhost:5432/continuum")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
EMBED_DIMENSION = int(os.getenv("EMBED_DIMENSION", "384"))

# Initialize embedding model
try:
    MODEL = SentenceTransformer(EMBED_MODEL)
    logger.info(f"Loaded embedding model: {EMBED_MODEL}")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    MODEL = None

# Pydantic models
class MemoryDoc(BaseModel):
    doc_id: str = Field(..., description="Unique document identifier")
    title: Optional[str] = Field(None, description="Document title")
    content: str = Field(..., description="Document content")
    scope: str = Field("global", description="Scope: global, project:<tag>, agent:<name>")
    doc_type: str = Field("note", description="Document type")
    source_uri: Optional[str] = Field(None, description="Source URI")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class KVStore(BaseModel):
    key: str = Field(..., description="Key for the value")
    value: Any = Field(..., description="Value to store")
    scope: str = Field("global", description="Scope: global, project:<tag>, agent:<name>")
    ttl_until: Optional[datetime] = Field(None, description="Time-to-live until")
    value_type: str = Field("string", description="Type of value")

class AgentRun(BaseModel):
    agent_run_id: str = Field(..., description="Unique agent run identifier")
    agent_name: str = Field(..., description="Name of the agent")
    agent_type: Optional[str] = Field(None, description="Type of agent")
    project_tag: Optional[str] = Field(None, description="Project tag")
    parent_run_id: Optional[str] = Field(None, description="Parent run ID")
    input: Optional[Dict[str, Any]] = Field(None, description="Input to the agent")
    output: Optional[Dict[str, Any]] = Field(None, description="Output from the agent")
    tools: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Tools used")
    model_config: Optional[Dict[str, Any]] = Field(None, description="Model configuration")
    tokens_used: Optional[Dict[str, int]] = Field(None, description="Token usage")
    cost: Optional[float] = Field(None, description="Cost in USD")
    status: str = Field("success", description="Run status")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Start time")
    ended_at: Optional[datetime] = Field(None, description="End time")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query")
    k: int = Field(5, description="Number of results to return")
    scope: Optional[str] = Field(None, description="Scope filter")
    min_confidence: float = Field(0.0, description="Minimum confidence score")

# Database connection helper
def get_db_connection(tenant_id: str):
    """Get database connection with tenant context set"""
    conn = psycopg2.connect(DB_DSN, cursor_factory=RealDictCursor)
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, true)", (tenant_id,))
    return conn

# Dependency for tenant header
def get_tenant_id(x_tenant_id: str = Header(..., description="Tenant ID")):
    if not x_tenant_id or x_tenant_id not in ['GSG', 'DEMO', 'SYSTEM']:
        raise HTTPException(status_code=400, detail="Invalid tenant ID")
    return x_tenant_id

# Memory Document endpoints
@app.post("/v1/memory/doc")
async def upsert_doc(
    item: MemoryDoc,
    tenant_id: str = Depends(get_tenant_id)
):
    """Upsert a memory document with vector embedding"""
    if not MODEL:
        raise HTTPException(status_code=500, detail="Embedding model not available")
    
    try:
        # Generate embedding
        embedding = MODEL.encode([item.content]).tolist()[0]
        
        with get_db_connection(tenant_id) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO core.memory_doc 
                    (doc_id, tenant_id, scope, title, content, embedding, doc_type, source_uri, meta)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (doc_id) DO UPDATE SET 
                        scope = EXCLUDED.scope,
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        doc_type = EXCLUDED.doc_type,
                        source_uri = EXCLUDED.source_uri,
                        meta = EXCLUDED.meta,
                        updated_at = NOW()
                """, (
                    item.doc_id, tenant_id, item.scope, item.title, item.content,
                    embedding, item.doc_type, item.source_uri, json.dumps(item.meta)
                ))
                conn.commit()
        
        return {"ok": True, "doc_id": item.doc_id, "embedding_dimension": len(embedding)}
        
    except Exception as e:
        logger.error(f"Failed to upsert document: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/v1/memory/search")
async def search_docs(
    q: str = Query(..., description="Search query"),
    k: int = Query(5, description="Number of results"),
    scope: Optional[str] = Query(None, description="Scope filter"),
    min_confidence: float = Query(0.0, description="Minimum confidence"),
    tenant_id: str = Depends(get_tenant_id)
):
    """Vector search over memory documents"""
    if not MODEL:
        raise HTTPException(status_code=500, detail="Embedding model not available")
    
    try:
        # Generate query embedding
        query_embedding = MODEL.encode([q]).tolist()[0]
        
        with get_db_connection(tenant_id) as conn:
            with conn.cursor() as cur:
                # Build query with scope filter
                query = """
                    SELECT doc_id, title, scope, meta, 
                           1 - (embedding <=> %s) as similarity
                    FROM core.memory_doc 
                    WHERE tenant_id = %s
                """
                params = [query_embedding, tenant_id]
                
                if scope:
                    query += " AND scope = %s"
                    params.append(scope)
                
                query += """
                    AND embedding IS NOT NULL
                    ORDER BY embedding <=> %s
                    LIMIT %s
                """
                params.extend([query_embedding, k])
                
                cur.execute(query, params)
                rows = cur.fetchall()
                
                # Filter by confidence and format results
                results = []
                for row in rows:
                    if row['similarity'] >= min_confidence:
                        results.append({
                            "doc_id": row['doc_id'],
                            "title": row['title'],
                            "scope": row['scope'],
                            "meta": row['meta'],
                            "score": float(row['similarity'])
                        })
                
                return {"results": results, "query": q, "total": len(results)}
                
    except Exception as e:
        logger.error(f"Failed to search documents: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# KV Store endpoints
@app.post("/v1/kv")
async def set_kv(
    item: KVStore,
    tenant_id: str = Depends(get_tenant_id)
):
    """Set a key-value pair"""
    try:
        with get_db_connection(tenant_id) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO core.memory_kv 
                    (key, tenant_id, scope, value, value_type, ttl_until)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (key) DO UPDATE SET 
                        value = EXCLUDED.value,
                        value_type = EXCLUDED.value_type,
                        ttl_until = EXCLUDED.ttl_until,
                        updated_at = NOW()
                """, (
                    item.key, tenant_id, item.scope, 
                    json.dumps(item.value), item.value_type, item.ttl_until
                ))
                conn.commit()
        
        return {"ok": True, "key": item.key}
        
    except Exception as e:
        logger.error(f"Failed to set KV: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/v1/kv/{key}")
async def get_kv(
    key: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """Get a value by key"""
    try:
        with get_db_connection(tenant_id) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT key, value, value_type, scope, ttl_until, created_at
                    FROM core.memory_kv 
                    WHERE key = %s AND tenant_id = %s
                    AND (ttl_until IS NULL OR ttl_until > NOW())
                """, (key, tenant_id))
                
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Key not found or expired")
                
                return {
                    "key": row['key'],
                    "value": json.loads(row['value']),
                    "value_type": row['value_type'],
                    "scope": row['scope'],
                    "ttl_until": row['ttl_until'],
                    "created_at": row['created_at']
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get KV: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Agent Run endpoints
@app.post("/v1/runs")
async def create_agent_run(
    run: AgentRun,
    tenant_id: str = Depends(get_tenant_id)
):
    """Create or update an agent run record"""
    try:
        with get_db_connection(tenant_id) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO core.agent_run 
                    (agent_run_id, tenant_id, agent_name, agent_type, project_tag,
                     parent_run_id, input, output, tools, model_config, tokens_used,
                     cost, status, started_at, ended_at, duration_ms, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (agent_run_id) DO UPDATE SET 
                        output = EXCLUDED.output,
                        tools = EXCLUDED.tools,
                        status = EXCLUDED.status,
                        ended_at = EXCLUDED.ended_at,
                        duration_ms = EXCLUDED.duration_ms,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                """, (
                    run.agent_run_id, tenant_id, run.agent_name, run.agent_type,
                    run.project_tag, run.parent_run_id, json.dumps(run.input),
                    json.dumps(run.output), json.dumps(run.tools),
                    json.dumps(run.model_config), json.dumps(run.tokens_used),
                    run.cost, run.status, run.started_at, run.ended_at,
                    run.duration_ms, json.dumps(run.metadata)
                ))
                conn.commit()
        
        return {"ok": True, "agent_run_id": run.agent_run_id}
        
    except Exception as e:
        logger.error(f"Failed to create agent run: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/v1/runs/{run_id}")
async def get_agent_run(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """Get an agent run by ID"""
    try:
        with get_db_connection(tenant_id) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM core.agent_run 
                    WHERE agent_run_id = %s AND tenant_id = %s
                """, (run_id, tenant_id))
                
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Agent run not found")
                
                # Convert row to dict and parse JSON fields
                result = dict(row)
                for field in ['input', 'output', 'tools', 'model_config', 'tokens_used', 'metadata']:
                    if result.get(field):
                        result[field] = json.loads(result[field])
                
                return result
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent run: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/v1/runs")
async def list_agent_runs(
    agent_name: Optional[str] = Query(None, description="Filter by agent name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    tenant_id: str = Depends(get_tenant_id)
):
    """List agent runs with optional filtering"""
    try:
        with get_db_connection(tenant_id) as conn:
            with conn.cursor() as cur:
                # Build query with filters
                query = "SELECT * FROM core.agent_run WHERE tenant_id = %s"
                params = [tenant_id]
                
                if agent_name:
                    query += " AND agent_name = %s"
                    params.append(agent_name)
                
                if status:
                    query += " AND status = %s"
                    params.append(status)
                
                query += " ORDER BY started_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cur.execute(query, params)
                rows = cur.fetchall()
                
                # Parse JSON fields
                results = []
                for row in rows:
                    result = dict(row)
                    for field in ['input', 'output', 'tools', 'model_config', 'tokens_used', 'metadata']:
                        if result.get(field):
                            result[field] = json.loads(result[field])
                    results.append(result)
                
                return {"runs": results, "total": len(results)}
                
    except Exception as e:
        logger.error(f"Failed to list agent runs: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with get_db_connection("SYSTEM") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        
        # Test embedding model
        model_status = "ok" if MODEL else "error"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "ok",
            "embedding_model": model_status,
            "version": "0.1.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)