{{ config(materialized='incremental', unique_key='event_id') }}

SELECT
  json_extract_scalar(_raw, '$.headers.tenant_id')        AS tenant_id,
  json_extract_scalar(_raw, '$.headers.project_tag')      AS project_tag,
  json_extract_scalar(_raw, '$.headers.agent_run_id')     AS agent_run_id,
  json_extract_scalar(_raw, '$.headers.occurred_at')      AS occurred_at,
  json_extract_scalar(_raw, '$.payload.shipment_code')    AS shipment_code,
  json_extract_scalar(_raw, '$.payload.batch_code')       AS batch_code,
  CAST(json_extract_scalar(_raw, '$.payload.leg_number') AS INTEGER) AS leg_number,
  json_extract_scalar(_raw, '$.payload.mode')             AS mode,
  json_extract_scalar(_raw, '$.payload.from_location.name') AS from_location,
  json_extract_scalar(_raw, '$.payload.to_location.name')   AS to_location,
  json_extract_scalar(_raw, '$.payload.from_location.code') AS from_code,
  json_extract_scalar(_raw, '$.payload.to_location.code')   AS to_code,
  CAST(json_extract_scalar(_raw, '$.payload.distance_km') AS DOUBLE) AS distance_km,
  CAST(json_extract_scalar(_raw, '$.payload.payload.mass_kg') AS DOUBLE) AS payload_mass_kg,
  CAST(json_extract_scalar(_raw, '$.payload.payload.volume_m3') AS DOUBLE) AS payload_volume_m3,
  json_extract_scalar(_raw, '$.payload.payload.commodity') AS commodity,
  json_extract_scalar(_raw, '$.payload.payload.hs_code') AS hs_code,
  json_extract_scalar(_raw, '$.payload.vehicle.class') AS vehicle_class,
  json_extract_scalar(_raw, '$.payload.vehicle.fuel_type') AS fuel_type,
  json_extract_scalar(_raw, '$.payload.vehicle.euro_standard') AS euro_standard,
  CAST(json_extract_scalar(_raw, '$.payload.vehicle.load_factor_pct') AS DOUBLE) AS load_factor_pct,
  json_extract_scalar(_raw, '$.payload.vehicle.backhaul') AS backhaul,
  json_extract_scalar(_raw, '$.payload.carrier.name') AS carrier_name,
  json_extract_scalar(_raw, '$.payload.carrier.code') AS carrier_code,
  json_extract_scalar(_raw, '$.payload.carrier.vessel_name') AS vessel_name,
  json_extract_scalar(_raw, '$.payload.carrier.flight_number') AS flight_number,
  json_extract_scalar(_raw, '$.payload.timing.scheduled_departure') AS scheduled_departure,
  json_extract_scalar(_raw, '$.payload.timing.actual_departure') AS actual_departure,
  json_extract_scalar(_raw, '$.payload.timing.scheduled_arrival') AS scheduled_arrival,
  json_extract_scalar(_raw, '$.payload.timing.actual_arrival') AS actual_arrival,
  CAST(json_extract_scalar(_raw, '$.payload.timing.duration_hours') AS DOUBLE) AS duration_hours,
  CAST(json_extract_scalar(_raw, '$.payload.emissions.co2e_kg') AS DOUBLE) AS co2e_kg,
  CAST(json_extract_scalar(_raw, '$.payload.emissions.ttw_kg') AS DOUBLE) AS ttw_kg,
  CAST(json_extract_scalar(_raw, '$.payload.emissions.wtt_kg') AS DOUBLE) AS wtt_kg,
  json_extract_scalar(_raw, '$.payload.emissions.calculation_method') AS calculation_method,
  json_extract_scalar(_raw, '$.payload.emissions.factor_source') AS factor_source,
  json_extract_scalar(_raw, '$.payload.emissions.rf_applied') AS rf_applied,
  json_extract_scalar(_raw, '$.payload.temperature.controlled') AS temperature_controlled,
  json_extract_scalar(_raw, '$.payload.temperature.range_celsius.min') AS temp_min_celsius,
  json_extract_scalar(_raw, '$.payload.temperature.range_celsius.max') AS temp_max_celsius,
  json_extract_scalar(_raw, '$.payload.status') AS status,
  event_id,
  _raw,
  CURRENT_TIMESTAMP AS _loaded_at

FROM read_parquet('s3://lake/bronze/topic=Continuum_Overworld.Atlas_Planner--Airfreight__KE-DE@v0.9.2.events/*/*/*/*.parquet')

{% if is_incremental() %}
  WHERE _loaded_at > (SELECT MAX(_loaded_at) FROM {{ this }})
{% endif %}