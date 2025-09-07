-- Agentic Memory Bank Schema
-- Shared memory for all agents (Orion, MAR, MCP, SCIP, Rank_AI)

-- 1) Durable KV Store for hot settings/prompts
CREATE TABLE core.memory_kv (
    key TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL, -- global | project:<tag> | agent:<name>
    value JSONB NOT NULL,
    value_type TEXT, -- string, number, object, array, prompt, config
    ttl_until TIMESTAMPTZ,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT,
    updated_by TEXT
);

-- 2) Embedding Store for documents and semantic search
CREATE TABLE core.memory_doc (
    doc_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL, -- global | project:<tag> | agent:<name>
    title TEXT,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI ada-002 dimension
    embedding_model TEXT DEFAULT 'ada-002',
    chunk_index INTEGER DEFAULT 0,
    parent_doc_id TEXT,
    doc_type TEXT, -- note, conversation, document, code, policy
    source_uri TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT
);

-- 3) Agent Run Traces for orchestration history
CREATE TABLE core.agent_run (
    agent_run_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    agent_type TEXT,
    project_tag TEXT,
    parent_run_id TEXT, -- For nested agent calls
    input JSONB,
    output JSONB,
    tools JSONB DEFAULT '[]', -- Array of tool calls with timings
    model_config JSONB, -- LLM settings used
    tokens_used JSONB, -- {prompt: N, completion: M, total: T}
    cost NUMERIC,
    status TEXT NOT NULL, -- pending, running, success, error, timeout
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    duration_ms INTEGER,
    metadata JSONB DEFAULT '{}'
);

-- 4) Agent Conversations for dialog history
CREATE TABLE core.memory_conversation (
    conversation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    agent_run_id TEXT REFERENCES core.agent_run(agent_run_id),
    role TEXT NOT NULL, -- system, user, assistant, function
    content TEXT,
    function_name TEXT,
    function_args JSONB,
    token_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5) Agent Insights (cross-project learnings)
CREATE TABLE core.memory_insight (
    insight_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    insight_type TEXT, -- pattern, anomaly, recommendation, learning
    title TEXT NOT NULL,
    description TEXT,
    confidence NUMERIC CHECK (confidence >= 0 AND confidence <= 1),
    supporting_evidence JSONB DEFAULT '[]', -- Array of doc_ids, run_ids
    tags TEXT[] DEFAULT '{}',
    agent_name TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6) Tool Registry and Usage
CREATE TABLE core.memory_tool (
    tool_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_name TEXT NOT NULL UNIQUE,
    tool_type TEXT, -- api, function, query, command
    description TEXT,
    input_schema JSONB,
    output_schema JSONB,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE core.memory_tool_usage (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_run_id TEXT REFERENCES core.agent_run(agent_run_id),
    tool_name TEXT NOT NULL,
    input JSONB,
    output JSONB,
    duration_ms INTEGER,
    status TEXT, -- success, error, timeout
    error_message TEXT,
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on memory tables
ALTER TABLE core.memory_kv ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.memory_doc ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.agent_run ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.memory_conversation ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.memory_insight ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Memory KV
CREATE POLICY memory_kv_tenant_isolation ON core.memory_kv
    USING (tenant_id = core.current_tenant_id() OR scope = 'global');

CREATE POLICY memory_kv_insert ON core.memory_kv
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- RLS Policies for Memory Docs
CREATE POLICY memory_doc_tenant_isolation ON core.memory_doc
    USING (tenant_id = core.current_tenant_id() OR scope = 'global');

CREATE POLICY memory_doc_insert ON core.memory_doc
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- RLS Policies for Agent Runs
CREATE POLICY agent_run_tenant_isolation ON core.agent_run
    USING (tenant_id = core.current_tenant_id());

CREATE POLICY agent_run_insert ON core.agent_run
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- RLS Policies for Conversations
CREATE POLICY conversation_tenant_isolation ON core.memory_conversation
    USING (tenant_id = core.current_tenant_id());

CREATE POLICY conversation_insert ON core.memory_conversation
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- RLS Policies for Insights
CREATE POLICY insight_tenant_isolation ON core.memory_insight
    USING (tenant_id = core.current_tenant_id() OR scope = 'global');

CREATE POLICY insight_insert ON core.memory_insight
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- Create indexes for performance
CREATE INDEX idx_memory_kv_tenant_scope ON core.memory_kv(tenant_id, scope);
CREATE INDEX idx_memory_kv_ttl ON core.memory_kv(ttl_until) WHERE ttl_until IS NOT NULL;

CREATE INDEX idx_memory_doc_tenant_scope ON core.memory_doc(tenant_id, scope);
CREATE INDEX idx_memory_doc_embedding ON core.memory_doc USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_memory_doc_type ON core.memory_doc(doc_type);
CREATE INDEX idx_memory_doc_parent ON core.memory_doc(parent_doc_id) WHERE parent_doc_id IS NOT NULL;

CREATE INDEX idx_agent_run_tenant ON core.agent_run(tenant_id);
CREATE INDEX idx_agent_run_agent ON core.agent_run(agent_name);
CREATE INDEX idx_agent_run_status ON core.agent_run(status);
CREATE INDEX idx_agent_run_started ON core.agent_run(started_at);
CREATE INDEX idx_agent_run_parent ON core.agent_run(parent_run_id) WHERE parent_run_id IS NOT NULL;

CREATE INDEX idx_conversation_run ON core.memory_conversation(agent_run_id);
CREATE INDEX idx_insight_tenant_scope ON core.memory_insight(tenant_id, scope);
CREATE INDEX idx_insight_type ON core.memory_insight(insight_type);
CREATE INDEX idx_insight_tags ON core.memory_insight USING gin(tags);

-- Helper functions for vector search
CREATE OR REPLACE FUNCTION core.search_memory_docs(
    p_embedding vector(1536),
    p_tenant_id TEXT,
    p_scope TEXT DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    doc_id TEXT,
    title TEXT,
    content TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        md.doc_id,
        md.title,
        md.content,
        1 - (md.embedding <=> p_embedding) AS similarity
    FROM core.memory_doc md
    WHERE md.tenant_id = p_tenant_id
        AND (p_scope IS NULL OR md.scope = p_scope)
        AND md.embedding IS NOT NULL
    ORDER BY md.embedding <=> p_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to get agent's recent context
CREATE OR REPLACE FUNCTION core.get_agent_context(
    p_agent_name TEXT,
    p_tenant_id TEXT,
    p_hours INTEGER DEFAULT 24
)
RETURNS JSONB AS $$
DECLARE
    v_context JSONB;
BEGIN
    SELECT jsonb_build_object(
        'recent_runs', (
            SELECT jsonb_agg(jsonb_build_object(
                'run_id', agent_run_id,
                'status', status,
                'started_at', started_at,
                'duration_ms', duration_ms
            ))
            FROM (
                SELECT agent_run_id, status, started_at, duration_ms
                FROM core.agent_run
                WHERE agent_name = p_agent_name
                    AND tenant_id = p_tenant_id
                    AND started_at > NOW() - INTERVAL '1 hour' * p_hours
                ORDER BY started_at DESC
                LIMIT 10
            ) r
        ),
        'recent_insights', (
            SELECT jsonb_agg(jsonb_build_object(
                'title', title,
                'description', description,
                'confidence', confidence
            ))
            FROM (
                SELECT title, description, confidence
                FROM core.memory_insight
                WHERE agent_name = p_agent_name
                    AND tenant_id = p_tenant_id
                    AND created_at > NOW() - INTERVAL '1 hour' * p_hours
                ORDER BY created_at DESC
                LIMIT 5
            ) i
        ),
        'active_settings', (
            SELECT jsonb_object_agg(key, value)
            FROM core.memory_kv
            WHERE tenant_id = p_tenant_id
                AND scope IN ('global', 'agent:' || p_agent_name)
                AND (ttl_until IS NULL OR ttl_until > NOW())
        )
    ) INTO v_context;
    
    RETURN v_context;
END;
$$ LANGUAGE plpgsql STABLE;

-- Trigger to update memory_kv version on update
CREATE OR REPLACE FUNCTION core.increment_kv_version()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        NEW.version = OLD.version + 1;
        NEW.updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_memory_kv_version 
    BEFORE UPDATE ON core.memory_kv
    FOR EACH ROW EXECUTE FUNCTION core.increment_kv_version();