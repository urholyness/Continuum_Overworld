{{ config(materialized='table') }}

WITH source AS (
    SELECT * FROM {{ ref('bronze_esg_metric_events') }}
),

cleaned AS (
    SELECT
        -- Primary keys and identifiers
        event_id,
        tenant_id,
        project_tag,
        agent_run_id,
        
        -- Organization and document references
        org_id,
        doc_id,
        document_title,
        document_type,
        reporting_year,
        source_uri,
        document_hash,
        
        -- Metric details
        metric_type,
        metric_name,
        metric_value,
        unit,
        period_start,
        period_end,
        
        -- Quality and provenance
        confidence,
        method,
        model_version,
        page_reference,
        text_snippet,
        
        -- Timestamps
        occurred_at,
        _loaded_at,
        
        -- Data quality flags
        CASE 
            WHEN metric_value IS NULL THEN 'missing_value'
            WHEN metric_value < 0 THEN 'negative_value'
            WHEN confidence < 0.5 THEN 'low_confidence'
            WHEN metric_type IS NULL THEN 'missing_type'
            ELSE 'valid'
        END AS data_quality_status,
        
        -- Business logic
        CASE 
            WHEN metric_type IN ('scope1', 'scope2', 'scope3') THEN 'emissions'
            WHEN metric_type LIKE '%water%' THEN 'water'
            WHEN metric_type LIKE '%waste%' THEN 'waste'
            WHEN metric_type LIKE '%energy%' THEN 'energy'
            ELSE 'other'
        END AS metric_category,
        
        -- Normalized values (convert to standard units)
        CASE 
            WHEN unit = 'tCO2e' THEN metric_value * 1000  -- Convert to kgCO2e
            WHEN unit = 'kgCO2e' THEN metric_value
            WHEN unit = 'gCO2e' THEN metric_value / 1000  -- Convert to kgCO2e
            ELSE metric_value
        END AS metric_value_kg_co2e,
        
        CASE 
            WHEN unit = 'tCO2e' THEN 'kgCO2e'
            WHEN unit = 'kgCO2e' THEN 'kgCO2e'
            WHEN unit = 'gCO2e' THEN 'kgCO2e'
            ELSE unit
        END AS normalized_unit
        
    FROM source
    WHERE 
        -- Filter out invalid records
        tenant_id IS NOT NULL
        AND doc_id IS NOT NULL
        AND metric_type IS NOT NULL
        AND metric_value IS NOT NULL
),

final AS (
    SELECT
        *,
        -- Add derived fields
        EXTRACT(YEAR FROM occurred_at) AS event_year,
        EXTRACT(MONTH FROM occurred_at) AS event_month,
        EXTRACT(DAY FROM occurred_at) AS event_day,
        
        -- Confidence-weighted value for aggregation
        metric_value * COALESCE(confidence, 1.0) AS confidence_weighted_value,
        
        -- Flag for high-impact metrics
        CASE 
            WHEN metric_value > 1000 AND unit = 'tCO2e' THEN true
            WHEN metric_value > 1000000 AND unit = 'kgCO2e' THEN true
            ELSE false
        END AS is_high_impact
        
    FROM cleaned
)

SELECT * FROM final