{{ config(materialized='table') }}

WITH source AS (
    SELECT * FROM {{ ref('bronze_agent_run_events') }}
),

cleaned AS (
    SELECT
        -- Primary keys and identifiers
        event_id,
        tenant_id,
        project_tag,
        agent_run_id,
        
        -- Agent details
        agent_name,
        agent_type,
        parent_run_id,
        
        -- Run status and timing
        status,
        started_at,
        ended_at,
        duration_ms,
        
        -- Input and output
        input_prompt,
        output_response,
        output_data,
        tools_json,
        
        -- Model configuration
        model_provider,
        model_name,
        model_temperature,
        model_max_tokens,
        
        -- Token usage
        tokens_prompt,
        tokens_completion,
        tokens_total,
        
        -- Cost and performance
        cost_usd,
        
        -- Memory operations
        kv_reads,
        kv_writes,
        doc_searches,
        doc_writes,
        insights_generated,
        
        -- Error handling
        error_message,
        error_type,
        error_stack_trace,
        error_retry_count,
        
        -- Metadata
        metadata,
        
        -- Timestamps
        occurred_at,
        _loaded_at,
        
        -- Data quality flags
        CASE 
            WHEN agent_name IS NULL THEN 'missing_agent'
            WHEN status IS NULL THEN 'missing_status'
            WHEN started_at IS NULL THEN 'missing_start_time'
            WHEN duration_ms < 0 THEN 'negative_duration'
            ELSE 'valid'
        END AS data_quality_status,
        
        -- Business logic
        CASE 
            WHEN agent_type = 'Reasoner' THEN 'analysis'
            WHEN agent_type = 'Predictor' THEN 'forecasting'
            WHEN agent_type = 'Broker' THEN 'coordination'
            WHEN agent_type = 'Orchestrator' THEN 'workflow'
            WHEN agent_type = 'Controller' THEN 'governance'
            ELSE 'other'
        END AS agent_category,
        
        -- Performance analysis
        CASE 
            WHEN duration_ms < 1000 THEN 'fast'
            WHEN duration_ms < 10000 THEN 'normal'
            WHEN duration_ms < 60000 THEN 'slow'
            ELSE 'very_slow'
        END AS performance_category,
        
        -- Cost analysis
        CASE 
            WHEN cost_usd IS NULL OR cost_usd = 0 THEN 'free'
            WHEN cost_usd < 0.01 THEN 'very_low'
            WHEN cost_usd < 0.10 THEN 'low'
            WHEN cost_usd < 1.00 THEN 'medium'
            ELSE 'high'
        END AS cost_category,
        
        -- Success rate analysis
        CASE 
            WHEN status = 'success' THEN 1
            WHEN status = 'error' THEN 0
            WHEN status = 'timeout' THEN 0
            WHEN status = 'cancelled' THEN 0
            ELSE NULL
        END AS success_indicator
        
    FROM source
    WHERE 
        -- Filter out invalid records
        tenant_id IS NOT NULL
        AND agent_name IS NOT NULL
        AND status IS NOT NULL
),

final AS (
    SELECT
        *,
        -- Add derived fields
        EXTRACT(YEAR FROM occurred_at) AS event_year,
        EXTRACT(MONTH FROM occurred_at) AS event_month,
        EXTRACT(DAY FROM occurred_at) AS event_day,
        
        -- Duration in seconds for easier analysis
        duration_ms / 1000.0 AS duration_seconds,
        
        -- Token efficiency (tokens per second)
        CASE 
            WHEN duration_seconds > 0 AND tokens_total IS NOT NULL
            THEN tokens_total / duration_seconds
            ELSE NULL
        END AS tokens_per_second,
        
        -- Cost per token
        CASE 
            WHEN tokens_total > 0 AND cost_usd > 0
            THEN cost_usd / tokens_total
            ELSE NULL
        END AS cost_per_token,
        
        -- Memory operation intensity
        CASE 
            WHEN duration_seconds > 0
            THEN (COALESCE(kv_reads, 0) + COALESCE(kv_writes, 0) + 
                  COALESCE(doc_searches, 0) + COALESCE(doc_writes, 0)) / duration_seconds
            ELSE NULL
        END AS memory_ops_per_second,
        
        -- Tool usage count (parse from JSON)
        CASE 
            WHEN tools_json IS NOT NULL AND tools_json != 'null'
            THEN JSON_ARRAY_LENGTH(CAST(tools_json AS JSON))
            ELSE 0
        END AS tools_used_count,
        
        -- Has parent run flag
        CASE 
            WHEN parent_run_id IS NOT NULL THEN true
            ELSE false
        END AS has_parent_run,
        
        -- Is root run flag
        CASE 
            WHEN parent_run_id IS NULL THEN true
            ELSE false
        END AS is_root_run
        
    FROM cleaned
)

SELECT * FROM final