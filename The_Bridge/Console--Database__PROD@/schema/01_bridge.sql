-- The_Bridge Control Plane Schema
-- Central governance and service registry

-- Tenants table (organizations)
CREATE TABLE bridge.tenants (
    tenant_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    display_name TEXT,
    classification bridge.data_classification DEFAULT 'green',
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT
);

-- Projects registry
CREATE TABLE bridge.projects (
    project_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL REFERENCES bridge.tenants(tenant_id),
    project_tag TEXT NOT NULL, -- e.g., "GSG-FB-2025-W34"
    name TEXT NOT NULL,
    division TEXT, -- Forge, Oracle, Atlas, etc.
    capability TEXT,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, project_tag)
);

-- Service accounts for systems
CREATE TABLE bridge.service_accounts (
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL REFERENCES bridge.tenants(tenant_id),
    account_name TEXT NOT NULL,
    agent_type TEXT, -- Orion, MAR, MCP, SCIP, etc.
    division TEXT,
    api_key_hash TEXT,
    permissions JSONB DEFAULT '[]',
    last_activity TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, account_name)
);

-- Contract registry for event schemas
CREATE TABLE bridge.contracts (
    contract_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contract_name TEXT NOT NULL, -- e.g., "esg.metric.v1"
    version INTEGER NOT NULL,
    schema_json JSONB NOT NULL,
    division TEXT,
    capability TEXT,
    is_active BOOLEAN DEFAULT true,
    deprecated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT,
    UNIQUE(contract_name, version)
);

-- Event registry for tracking
CREATE TABLE bridge.event_registry (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    contract_name TEXT,
    version INTEGER,
    tenant_id TEXT REFERENCES bridge.tenants(tenant_id),
    project_tag TEXT,
    agent_run_id TEXT,
    occurred_at TIMESTAMPTZ NOT NULL,
    ingested_at TIMESTAMPTZ DEFAULT NOW(),
    payload JSONB,
    headers JSONB,
    status core.event_status DEFAULT 'pending',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    FOREIGN KEY (contract_name, version) REFERENCES bridge.contracts(contract_name, version)
);

-- Agent registry
CREATE TABLE bridge.agents (
    agent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL UNIQUE,
    agent_type TEXT, -- Reasoner, Planner, Ingestor, Calculator, etc.
    division TEXT NOT NULL,
    capability TEXT,
    role TEXT,
    qualifier TEXT,
    version TEXT,
    status bridge.agent_status DEFAULT 'active',
    config JSONB DEFAULT '{}',
    capabilities JSONB DEFAULT '[]', -- List of capabilities
    dependencies JSONB DEFAULT '[]', -- Other agents it depends on
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data lineage tracking
CREATE TABLE bridge.lineage (
    lineage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    source_type TEXT NOT NULL, -- table, topic, file, api
    source_name TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_name TEXT NOT NULL,
    transformation TEXT,
    agent_name TEXT,
    job_id TEXT,
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Governance policies
CREATE TABLE bridge.policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_name TEXT NOT NULL UNIQUE,
    policy_type TEXT NOT NULL, -- rls, classification, retention, access
    scope TEXT NOT NULL, -- schema, table, column
    target TEXT NOT NULL, -- specific schema.table or schema.table.column
    rules JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT
);

-- Create indexes
CREATE INDEX idx_projects_tenant ON bridge.projects(tenant_id);
CREATE INDEX idx_projects_tag ON bridge.projects(project_tag);
CREATE INDEX idx_service_accounts_tenant ON bridge.service_accounts(tenant_id);
CREATE INDEX idx_contracts_name ON bridge.contracts(contract_name);
CREATE INDEX idx_event_registry_type ON bridge.event_registry(event_type);
CREATE INDEX idx_event_registry_tenant ON bridge.event_registry(tenant_id);
CREATE INDEX idx_event_registry_occurred ON bridge.event_registry(occurred_at);
CREATE INDEX idx_agents_division ON bridge.agents(division);
CREATE INDEX idx_lineage_tenant ON bridge.lineage(tenant_id);
CREATE INDEX idx_lineage_source ON bridge.lineage(source_type, source_name);
CREATE INDEX idx_lineage_target ON bridge.lineage(target_type, target_name);

-- Insert default tenants
INSERT INTO bridge.tenants (tenant_id, name, display_name) VALUES
    ('GSG', 'GreenStemGlobal', 'GreenStem Global Ltd'),
    ('DEMO', 'Demo', 'Demo Organization'),
    ('SYSTEM', 'System', 'System Internal');

-- Insert default agents
INSERT INTO bridge.agents (agent_name, agent_type, division, capability, status) VALUES
    ('Bridge_Controller', 'Controller', 'The_Bridge', 'Orchestration', 'active'),
    ('Orion_Reasoner', 'Reasoner', 'Orion', 'Analysis', 'active'),
    ('MAR_Omen', 'Predictor', 'MAR', 'Forecasting', 'active'),
    ('MCP_Broker', 'Broker', 'MCP', 'Coordination', 'active'),
    ('SCIP_Orchestrator', 'Orchestrator', 'SCIP', 'Workflow', 'active'),
    ('Forge_Ingestor', 'Ingestor', 'Forge', 'DataIngestion', 'active'),
    ('Oracle_Calculator', 'Calculator', 'Oracle', 'Computation', 'active'),
    ('Atlas_Planner', 'Planner', 'Atlas', 'Logistics', 'active');

-- Add audit triggers
CREATE TRIGGER trg_tenants_audit BEFORE INSERT OR UPDATE ON bridge.tenants
    FOR EACH ROW EXECUTE FUNCTION audit.track_changes();

CREATE TRIGGER trg_projects_audit BEFORE INSERT OR UPDATE ON bridge.projects
    FOR EACH ROW EXECUTE FUNCTION audit.track_changes();

CREATE TRIGGER trg_agents_audit BEFORE INSERT OR UPDATE ON bridge.agents
    FOR EACH ROW EXECUTE FUNCTION audit.track_changes();