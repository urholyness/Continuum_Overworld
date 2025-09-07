-- Incremental processing helpers for Continuum_Overworld

{% macro get_lake_path(layer, topic) %}
    {% set bucket = var('lake_bucket', 'lake') %}
    {% set path = var(layer ~ '_path', layer) %}
    {% set full_path = 's3://' ~ bucket ~ '/' ~ path ~ '/topic=' ~ topic ~ '/*/*/*/*.parquet' %}
    {{ return(full_path) }}
{% endmacro %}

{% macro get_partition_filter(date_column, lookback_hours) %}
    {% if is_incremental() %}
        WHERE {{ date_column }} >= CURRENT_TIMESTAMP - INTERVAL '{{ lookback_hours }}' HOUR
    {% endif %}
{% endmacro %}

{% macro validate_tenant_id(tenant_column) %}
    CASE 
        WHEN {{ tenant_column }} IS NULL THEN false
        WHEN {{ tenant_column }} = '' THEN false
        WHEN {{ tenant_column }} NOT IN ('GSG', 'DEMO', 'SYSTEM') THEN false
        ELSE true
    END
{% endmacro %}

{% macro data_quality_check(table_name) %}
    -- Common data quality checks for Continuum_Overworld tables
    SELECT 
        COUNT(*) as total_rows,
        COUNT(CASE WHEN tenant_id IS NULL THEN 1 END) as missing_tenant_id,
        COUNT(CASE WHEN tenant_id NOT IN ('GSG', 'DEMO', 'SYSTEM') THEN 1 END) as invalid_tenant_id,
        COUNT(CASE WHEN created_at IS NULL THEN 1 END) as missing_created_at,
        COUNT(CASE WHEN created_at > CURRENT_TIMESTAMP THEN 1 END) as future_created_at,
        CURRENT_TIMESTAMP as check_timestamp
    FROM {{ table_name }}
{% endmacro %}

{% macro incremental_merge_strategy() %}
    {% if target.type == 'duckdb' %}
        -- DuckDB merge strategy
        MERGE INTO {{ this }} AS target
        USING {{ source }} AS source
        ON target.event_id = source.event_id
        WHEN MATCHED THEN
            UPDATE SET 
                updated_at = CURRENT_TIMESTAMP,
                -- Add other fields to update
        WHEN NOT MATCHED THEN
            INSERT (/* column list */)
            VALUES (/* value list */)
    {% else %}
        -- Standard incremental strategy for other databases
        {{ config(materialized='incremental') }}
    {% endif %}
{% endmacro %}

{% macro add_audit_columns() %}
    -- Add standard audit columns to tables
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255),
    version INTEGER DEFAULT 1
{% endmacro %}

{% macro add_tenant_columns() %}
    -- Add standard tenant columns to tables
    tenant_id VARCHAR(10) NOT NULL,
    project_tag VARCHAR(100),
    org_id UUID
{% endmacro %}

{% macro add_provenance_columns() %}
    -- Add standard provenance columns for data lineage
    source_uri TEXT,
    method VARCHAR(255),
    model_version VARCHAR(50),
    confidence DECIMAL(3,2),
    doc_id TEXT
{% endmacro %}

