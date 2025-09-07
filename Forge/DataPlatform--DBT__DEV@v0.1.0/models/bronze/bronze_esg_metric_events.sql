{{ config(materialized='incremental', unique_key='event_id') }}

SELECT
  json_extract_scalar(_raw, '$.headers.tenant_id')        AS tenant_id,
  json_extract_scalar(_raw, '$.headers.project_tag')      AS project_tag,
  json_extract_scalar(_raw, '$.headers.agent_run_id')     AS agent_run_id,
  json_extract_scalar(_raw, '$.headers.occurred_at')      AS occurred_at,
  json_extract_scalar(_raw, '$.payload.org_id')           AS org_id,
  json_extract_scalar(_raw, '$.payload.doc_id')           AS doc_id,
  json_extract_scalar(_raw, '$.payload.metrics[0].metric_type')  AS metric_type,
  json_extract_scalar(_raw, '$.payload.metrics[0].metric_name')  AS metric_name,
  CAST(json_extract_scalar(_raw, '$.payload.metrics[0].value') AS DOUBLE) AS metric_value,
  json_extract_scalar(_raw, '$.payload.metrics[0].unit')     AS unit,
  CAST(json_extract_scalar(_raw, '$.payload.metrics[0].period_start') AS DATE) AS period_start,
  CAST(json_extract_scalar(_raw, '$.payload.metrics[0].period_end') AS DATE) AS period_end,
  CAST(json_extract_scalar(_raw, '$.payload.metrics[0].confidence') AS DOUBLE) AS confidence,
  json_extract_scalar(_raw, '$.payload.metrics[0].method')   AS method,
  json_extract_scalar(_raw, '$.payload.metrics[0].model_version') AS model_version,
  json_extract_scalar(_raw, '$.payload.metrics[0].page_reference') AS page_reference,
  json_extract_scalar(_raw, '$.payload.metrics[0].text_snippet') AS text_snippet,
  json_extract_scalar(_raw, '$.payload.document_metadata.title') AS document_title,
  json_extract_scalar(_raw, '$.payload.document_metadata.document_type') AS document_type,
  CAST(json_extract_scalar(_raw, '$.payload.document_metadata.reporting_year') AS INTEGER) AS reporting_year,
  json_extract_scalar(_raw, '$.payload.document_metadata.source_uri') AS source_uri,
  json_extract_scalar(_raw, '$.payload.document_metadata.hash') AS document_hash,
  event_id,
  _raw,
  CURRENT_TIMESTAMP AS _loaded_at

FROM read_parquet('s3://lake/bronze/topic=Continuum_Overworld.Oracle_Calculator--ESG__PROD@v1.events/*/*/*/*.parquet')

{% if is_incremental() %}
  WHERE _loaded_at > (SELECT MAX(_loaded_at) FROM {{ this }})
{% endif %}