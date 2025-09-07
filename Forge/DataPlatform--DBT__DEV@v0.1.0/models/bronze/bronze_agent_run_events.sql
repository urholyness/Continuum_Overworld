{{ config(materialized='incremental', unique_key='event_id') }}

SELECT
  json_extract_scalar(_raw, '$.headers.tenant_id')        AS tenant_id,
  json_extract_scalar(_raw, '$.headers.project_tag')      AS project_tag,
  json_extract_scalar(_raw, '$.headers.agent_run_id')     AS agent_run_id,
  json_extract_scalar(_raw, '$.headers.occurred_at')      AS occurred_at,
  json_extract_scalar(_raw, '$.payload.agent_name')       AS agent_name,
  json_extract_scalar(_raw, '$.payload.agent_type')       AS agent_type,
  json_extract_scalar(_raw, '$.payload.parent_run_id')    AS parent_run_id,
  json_extract_scalar(_raw, '$.payload.status')           AS status,
  json_extract_scalar(_raw, '$.payload.started_at')       AS started_at,
  json_extract_scalar(_raw, '$.payload.ended_at')         AS ended_at,
  CAST(json_extract_scalar(_raw, '$.payload.duration_ms') AS INTEGER) AS duration_ms,
  json_extract_scalar(_raw, '$.payload.input.prompt')     AS input_prompt,
  json_extract_scalar(_raw, '$.payload.output.response')  AS output_response,
  json_extract_scalar(_raw, '$.payload.output.data')      AS output_data,
  json_extract_scalar(_raw, '$.payload.tools')            AS tools_json,
  json_extract_scalar(_raw, '$.payload.model_config.provider') AS model_provider,
  json_extract_scalar(_raw, '$.payload.model_config.model') AS model_name,
  CAST(json_extract_scalar(_raw, '$.payload.model_config.temperature') AS DOUBLE) AS model_temperature,
  CAST(json_extract_scalar(_raw, '$.payload.model_config.max_tokens') AS INTEGER) AS model_max_tokens,
  json_extract_scalar(_raw, '$.payload.tokens_used.prompt') AS tokens_prompt,
  json_extract_scalar(_raw, '$.payload.tokens_used.completion') AS tokens_completion,
  json_extract_scalar(_raw, '$.payload.tokens_used.total') AS tokens_total,
  CAST(json_extract_scalar(_raw, '$.payload.cost') AS DOUBLE) AS cost_usd,
  json_extract_scalar(_raw, '$.payload.memory_operations.kv_reads') AS kv_reads,
  json_extract_scalar(_raw, '$.payload.memory_operations.kv_writes') AS kv_writes,
  json_extract_scalar(_raw, '$.payload.memory_operations.doc_searches') AS doc_searches,
  json_extract_scalar(_raw, '$.payload.memory_operations.doc_writes') AS doc_writes,
  json_extract_scalar(_raw, '$.payload.memory_operations.insights_generated') AS insights_generated,
  json_extract_scalar(_raw, '$.payload.error.message') AS error_message,
  json_extract_scalar(_raw, '$.payload.error.type') AS error_type,
  json_extract_scalar(_raw, '$.payload.error.stack_trace') AS error_stack_trace,
  CAST(json_extract_scalar(_raw, '$.payload.error.retry_count') AS INTEGER) AS error_retry_count,
  json_extract_scalar(_raw, '$.payload.metadata') AS metadata,
  event_id,
  _raw,
  CURRENT_TIMESTAMP AS _loaded_at

FROM read_parquet('s3://lake/bronze/topic=Continuum_Overworld.Orion_Reasoner--Analysis__PROD@v1.events/*/*/*/*.parquet')

{% if is_incremental() %}
  WHERE _loaded_at > (SELECT MAX(_loaded_at) FROM {{ this }})
{% endif %}