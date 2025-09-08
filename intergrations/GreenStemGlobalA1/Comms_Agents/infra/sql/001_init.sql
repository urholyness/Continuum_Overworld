-- Initialize Comms Agents Database
-- This file creates all necessary tables for the system

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Posts table for scheduled and published content
CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform TEXT NOT NULL CHECK (platform IN ('linkedin', 'twitter', 'email', 'buffer')),
    content TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'published', 'failed')),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}'
);

-- Approvals table for human approval workflow
CREATE TABLE IF NOT EXISTS approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    approver_id TEXT,
    approved BOOLEAN,
    approved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Events table for system events and logging
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kind TEXT NOT NULL,
    source TEXT NOT NULL,
    payload JSONB DEFAULT '{}',
    severity TEXT DEFAULT 'info' CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Campaigns table for organized content campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')),
    start_date DATE,
    end_date DATE,
    meta JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Risk logs table for compliance and risk tracking
CREATE TABLE IF NOT EXISTS risk_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    level TEXT NOT NULL CHECK (level IN ('green', 'amber', 'red')),
    category TEXT NOT NULL,
    notes JSONB DEFAULT '{}',
    reviewed_by TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge base table for RAG content
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_path TEXT,
    source_type TEXT CHECK (source_type IN ('issue_card', 'document', 'web', 'manual')),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    embedding_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Issue cards table for topic management
CREATE TABLE IF NOT EXISTS issue_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    content TEXT NOT NULL,
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status TEXT DEFAULT 'active' CHECK (status IN ('draft', 'active', 'archived', 'deprecated')),
    tags TEXT[] DEFAULT '{}',
    sources TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent runs table for tracking agent executions
CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL,
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    status TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    execution_time_ms INTEGER,
    metadata JSONB DEFAULT '{}'
);

-- Workflows table for orchestrated agent chains
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    steps JSONB NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'deprecated')),
    schedule_cron TEXT,
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workflow runs table for tracking workflow executions
CREATE TABLE IF NOT EXISTS workflow_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    results JSONB DEFAULT '{}',
    error_message TEXT,
    execution_time_ms INTEGER
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform);
CREATE INDEX IF NOT EXISTS idx_posts_scheduled_at ON posts(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_events_kind ON events(kind);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_base USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_issue_cards_tags ON issue_cards USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_agent_runs_agent_name ON agent_runs(agent_name);
CREATE INDEX IF NOT EXISTS idx_workflows_schedule ON workflows(schedule_cron);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_issue_cards_updated_at BEFORE UPDATE ON issue_cards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO issue_cards (title, summary, content, priority, tags, sources) VALUES
(
    'EUDR & Kenyan Smallholders: Risk, Readiness, Opportunity',
    'EU deforestation rules reshape procurement; Kenyan smallholders risk exclusion without traceability. Bridge: cooperative traceability + exporter QA + diaspora-backed upgrades.',
    'EUDR & Kenyan Smallholders: Risk, Readiness, Opportunity

EU deforestation rules reshape procurement; Kenyan smallholders risk exclusion without traceability. Bridge: cooperative traceability + exporter QA + diaspora-backed upgrades.

https://environment.ec.europa.eu/publications/eu-deforestation-regulation_en',
    'high',
    ARRAY['EUDR', 'Kenya', 'smallholders', 'traceability', 'trade'],
    ARRAY['https://environment.ec.europa.eu/publications/eu-deforestation-regulation_en']
),
(
    'Mechanization-as-a-Service for East African Smallholders',
    'Per-acre cost drops with shared CAPEX; uptime + operator training drive ROI; bundling with offtake reduces price risk.',
    'Mechanization-as-a-Service for East African Smallholders

Per-acre cost drops with shared CAPEX; uptime + operator training drive ROI; bundling with offtake reduces price risk.',
    'medium',
    ARRAY['mechanization', 'East Africa', 'smallholders', 'CAPEX', 'ROI'],
    ARRAY[]
);

-- Insert sample campaign
INSERT INTO campaigns (name, description, status, start_date, end_date, meta) VALUES
(
    'EUDR Awareness Campaign',
    'Educational campaign about EU Deforestation Regulation impact on African agriculture',
    'active',
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '30 days',
    '{"target_audience": ["buyers", "policy_makers"], "platforms": ["linkedin", "twitter"]}'
);

