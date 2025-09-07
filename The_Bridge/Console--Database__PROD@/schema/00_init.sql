-- The_Bridge Database Foundation
-- Initialization script for multi-tenant control plane
-- Version: 0.1.0

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS bridge;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS reference;
CREATE SCHEMA IF NOT EXISTS pii;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set search path
ALTER DATABASE continuum SET search_path TO core, bridge, reference, public;

-- Create custom types
CREATE TYPE bridge.agent_status AS ENUM ('active', 'inactive', 'suspended', 'deprecated');
CREATE TYPE bridge.data_classification AS ENUM ('green', 'amber', 'red', 'black');
CREATE TYPE core.event_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'archived');

-- Grant schema permissions
GRANT USAGE ON SCHEMA bridge TO PUBLIC;
GRANT USAGE ON SCHEMA core TO PUBLIC;
GRANT USAGE ON SCHEMA reference TO PUBLIC;

-- Create application roles
CREATE ROLE app_reader;
CREATE ROLE app_writer;
CREATE ROLE app_admin;
CREATE ROLE app_agent;

-- Grant base permissions
GRANT USAGE ON SCHEMA core TO app_reader, app_writer, app_admin, app_agent;
GRANT USAGE ON SCHEMA bridge TO app_reader, app_writer, app_admin, app_agent;
GRANT USAGE ON SCHEMA reference TO app_reader, app_writer, app_admin, app_agent;

-- Reader can only SELECT
GRANT SELECT ON ALL TABLES IN SCHEMA core TO app_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA bridge TO app_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA reference TO app_reader;

-- Writer can INSERT, UPDATE, DELETE in core
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA core TO app_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA bridge TO app_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA reference TO app_writer;

-- Admin has full access
GRANT ALL PRIVILEGES ON SCHEMA core TO app_admin;
GRANT ALL PRIVILEGES ON SCHEMA bridge TO app_admin;
GRANT ALL PRIVILEGES ON SCHEMA reference TO app_admin;

-- Agent role for AI systems
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA core TO app_agent;
GRANT SELECT ON ALL TABLES IN SCHEMA bridge TO app_agent;
GRANT SELECT ON ALL TABLES IN SCHEMA reference TO app_agent;

-- Create tenant-specific roles (examples)
CREATE ROLE app_gsg WITH LOGIN PASSWORD 'gsg_secure_2025' IN ROLE app_writer;
CREATE ROLE app_demo WITH LOGIN PASSWORD 'demo_secure_2025' IN ROLE app_writer;

-- Audit function for tracking changes
CREATE OR REPLACE FUNCTION audit.track_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.created_at = COALESCE(NEW.created_at, NOW());
        NEW.created_by = COALESCE(NEW.created_by, current_setting('app.user_id', true));
        NEW.updated_at = NEW.created_at;
        NEW.updated_by = NEW.created_by;
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at = NOW();
        NEW.updated_by = current_setting('app.user_id', true);
        NEW.created_at = OLD.created_at;
        NEW.created_by = OLD.created_by;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- RLS helper function
CREATE OR REPLACE FUNCTION core.current_tenant_id()
RETURNS TEXT AS $$
BEGIN
    RETURN current_setting('app.tenant_id', true);
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Event versioning function
CREATE OR REPLACE FUNCTION bridge.next_event_version(p_event_type TEXT)
RETURNS INTEGER AS $$
DECLARE
    v_version INTEGER;
BEGIN
    SELECT COALESCE(MAX(version), 0) + 1
    INTO v_version
    FROM bridge.event_registry
    WHERE event_type = p_event_type;
    
    RETURN v_version;
END;
$$ LANGUAGE plpgsql;