-- Core Multi-Tenant Schema with RLS
-- Business entities and operational data

-- Organizations
CREATE TABLE core.org (
    org_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    org_code TEXT NOT NULL,
    org_name TEXT NOT NULL,
    org_type TEXT, -- supplier, customer, partner, subsidiary
    country_code TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, org_code)
);

-- Documents (CSR reports, invoices, etc.)
CREATE TABLE core.document (
    doc_id TEXT PRIMARY KEY, -- Can be hash or structured ID
    tenant_id TEXT NOT NULL,
    project_tag TEXT,
    doc_type TEXT NOT NULL, -- csr_report, invoice, shipment_doc, certificate
    title TEXT,
    source_uri TEXT, -- S3/MinIO path
    content_hash TEXT,
    extracted_text TEXT,
    metadata JSONB DEFAULT '{}',
    processing_status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ESG Metrics (extracted from documents)
CREATE TABLE core.esg_metric (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    doc_id TEXT REFERENCES core.document(doc_id),
    org_id UUID REFERENCES core.org(org_id),
    metric_type TEXT NOT NULL, -- scope1, scope2, scope3_cat4, water, waste, etc.
    metric_name TEXT NOT NULL,
    value NUMERIC,
    unit TEXT,
    period_start DATE,
    period_end DATE,
    confidence NUMERIC CHECK (confidence >= 0 AND confidence <= 1),
    method TEXT, -- extraction_method
    model_version TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Batches (shipment batches)
CREATE TABLE core.batch (
    batch_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    project_tag TEXT,
    batch_code TEXT NOT NULL,
    commodity TEXT,
    net_mass_kg NUMERIC,
    packaging_mass_kg NUMERIC,
    harvest_week TEXT,
    origin_location TEXT,
    destination_location TEXT,
    ownership TEXT, -- own, 3pl
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, batch_code)
);

-- Shipments
CREATE TABLE core.shipment (
    shipment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    batch_id UUID REFERENCES core.batch(batch_id),
    shipment_code TEXT NOT NULL,
    mode TEXT NOT NULL, -- truck, air, rail, sea, barge
    from_location TEXT NOT NULL,
    to_location TEXT NOT NULL,
    distance_km NUMERIC,
    payload_tonnes NUMERIC,
    vehicle_class TEXT,
    departure_date DATE,
    arrival_date DATE,
    carrier_name TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, shipment_code)
);

-- Emissions Events
CREATE TABLE core.emissions_event (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    shipment_id UUID REFERENCES core.shipment(shipment_id),
    batch_id UUID REFERENCES core.batch(batch_id),
    emission_type TEXT NOT NULL, -- transport, energy, process
    emission_scope TEXT, -- scope1, scope2, scope3
    emission_category TEXT, -- cat4_upstream, cat9_downstream
    co2e_kg NUMERIC NOT NULL,
    ttw_kg NUMERIC, -- Tank-to-Wheel
    wtt_kg NUMERIC, -- Well-to-Tank
    calculation_method TEXT,
    factor_source TEXT,
    factor_version TEXT,
    metadata JSONB DEFAULT '{}',
    occurred_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Partner opportunities (for Rank_AI)
CREATE TABLE core.partner_opportunity (
    opportunity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    org_id UUID REFERENCES core.org(org_id),
    opportunity_type TEXT, -- sustainability, cost_reduction, efficiency
    score NUMERIC,
    rationale TEXT,
    suggested_actions JSONB DEFAULT '[]',
    agent_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on all core tables
ALTER TABLE core.org ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.document ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.esg_metric ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.batch ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.shipment ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.emissions_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.partner_opportunity ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for each table
-- Organizations
CREATE POLICY org_tenant_isolation ON core.org
    USING (tenant_id = core.current_tenant_id());

CREATE POLICY org_insert ON core.org
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- Documents
CREATE POLICY document_tenant_isolation ON core.document
    USING (tenant_id = core.current_tenant_id());

CREATE POLICY document_insert ON core.document
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- ESG Metrics
CREATE POLICY esg_metric_tenant_isolation ON core.esg_metric
    USING (tenant_id = core.current_tenant_id());

CREATE POLICY esg_metric_insert ON core.esg_metric
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- Batches
CREATE POLICY batch_tenant_isolation ON core.batch
    USING (tenant_id = core.current_tenant_id());

CREATE POLICY batch_insert ON core.batch
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- Shipments
CREATE POLICY shipment_tenant_isolation ON core.shipment
    USING (tenant_id = core.current_tenant_id());

CREATE POLICY shipment_insert ON core.shipment
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- Emissions Events
CREATE POLICY emissions_tenant_isolation ON core.emissions_event
    USING (tenant_id = core.current_tenant_id());

CREATE POLICY emissions_insert ON core.emissions_event
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- Partner Opportunities
CREATE POLICY partner_tenant_isolation ON core.partner_opportunity
    USING (tenant_id = core.current_tenant_id());

CREATE POLICY partner_insert ON core.partner_opportunity
    FOR INSERT WITH CHECK (tenant_id = core.current_tenant_id());

-- Create indexes for performance
CREATE INDEX idx_org_tenant ON core.org(tenant_id);
CREATE INDEX idx_document_tenant ON core.document(tenant_id);
CREATE INDEX idx_document_type ON core.document(doc_type);
CREATE INDEX idx_esg_metric_tenant ON core.esg_metric(tenant_id);
CREATE INDEX idx_esg_metric_type ON core.esg_metric(metric_type);
CREATE INDEX idx_batch_tenant ON core.batch(tenant_id);
CREATE INDEX idx_shipment_tenant ON core.shipment(tenant_id);
CREATE INDEX idx_emissions_tenant ON core.emissions_event(tenant_id);
CREATE INDEX idx_partner_tenant ON core.partner_opportunity(tenant_id);

-- Add audit triggers
CREATE TRIGGER trg_org_audit BEFORE INSERT OR UPDATE ON core.org
    FOR EACH ROW EXECUTE FUNCTION audit.track_changes();

CREATE TRIGGER trg_document_audit BEFORE INSERT OR UPDATE ON core.document
    FOR EACH ROW EXECUTE FUNCTION audit.track_changes();

CREATE TRIGGER trg_batch_audit BEFORE INSERT OR UPDATE ON core.batch
    FOR EACH ROW EXECUTE FUNCTION audit.track_changes();