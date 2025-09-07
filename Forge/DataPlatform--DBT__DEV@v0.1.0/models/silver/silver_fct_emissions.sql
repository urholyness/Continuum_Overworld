{{ config(materialized='table') }}

WITH source AS (
    SELECT * FROM {{ ref('bronze_shipment_leg_events') }}
),

cleaned AS (
    SELECT
        -- Primary keys and identifiers
        event_id,
        tenant_id,
        project_tag,
        agent_run_id,
        
        -- Shipment and batch references
        shipment_code,
        batch_code,
        leg_number,
        
        -- Transport details
        mode,
        from_location,
        to_location,
        from_code,
        to_code,
        distance_km,
        
        -- Payload information
        payload_mass_kg,
        payload_volume_m3,
        commodity,
        hs_code,
        
        -- Vehicle specifications
        vehicle_class,
        fuel_type,
        euro_standard,
        load_factor_pct,
        backhaul,
        
        -- Carrier information
        carrier_name,
        carrier_code,
        vessel_name,
        flight_number,
        
        -- Timing
        scheduled_departure,
        actual_departure,
        scheduled_arrival,
        actual_arrival,
        duration_hours,
        
        -- Emissions data
        co2e_kg,
        ttw_kg,
        wtt_kg,
        calculation_method,
        factor_source,
        rf_applied,
        
        -- Temperature control
        temperature_controlled,
        temp_min_celsius,
        temp_max_celsius,
        
        -- Status
        status,
        
        -- Timestamps
        occurred_at,
        _loaded_at,
        
        -- Data quality flags
        CASE 
            WHEN co2e_kg IS NULL THEN 'missing_emissions'
            WHEN co2e_kg < 0 THEN 'negative_emissions'
            WHEN distance_km < 0 THEN 'negative_distance'
            WHEN payload_mass_kg < 0 THEN 'negative_mass'
            ELSE 'valid'
        END AS data_quality_status,
        
        -- Business logic
        CASE 
            WHEN mode = 'truck' THEN 'road'
            WHEN mode = 'rail' THEN 'rail'
            WHEN mode = 'air' THEN 'air'
            WHEN mode = 'sea' THEN 'maritime'
            WHEN mode = 'barge' THEN 'inland_water'
            ELSE 'other'
        END AS transport_category,
        
        -- Emissions intensity (kgCO2e per tonne-km)
        CASE 
            WHEN payload_mass_kg > 0 AND distance_km > 0 
            THEN co2e_kg / (payload_mass_kg / 1000) / distance_km
            ELSE NULL
        END AS emissions_intensity_kg_co2e_per_tkm,
        
        -- Load factor analysis
        CASE 
            WHEN load_factor_pct >= 80 THEN 'high'
            WHEN load_factor_pct >= 50 THEN 'medium'
            WHEN load_factor_pct > 0 THEN 'low'
            ELSE 'unknown'
        END AS load_factor_category,
        
        -- Route efficiency
        CASE 
            WHEN distance_km > 0 AND payload_mass_kg > 0
            THEN (payload_mass_kg / 1000) / distance_km  -- tonnes per km
            ELSE NULL
        END AS payload_density_t_per_km
        
    FROM source
    WHERE 
        -- Filter out invalid records
        tenant_id IS NOT NULL
        AND shipment_code IS NOT NULL
        AND mode IS NOT NULL
        AND from_location IS NOT NULL
        AND to_location IS NOT NULL
),

final AS (
    SELECT
        *,
        -- Add derived fields
        EXTRACT(YEAR FROM occurred_at) AS event_year,
        EXTRACT(MONTH FROM occurred_at) AS event_month,
        EXTRACT(DAY FROM occurred_at) AS event_day,
        
        -- Time performance metrics
        CASE 
            WHEN actual_departure IS NOT NULL AND scheduled_departure IS NOT NULL
            THEN EXTRACT(EPOCH FROM (actual_departure - scheduled_departure)) / 3600
            ELSE NULL
        END AS departure_delay_hours,
        
        CASE 
            WHEN actual_arrival IS NOT NULL AND scheduled_arrival IS NOT NULL
            THEN EXTRACT(EPOCH FROM (actual_arrival - scheduled_arrival)) / 3600
            ELSE NULL
        END AS arrival_delay_hours,
        
        -- Emissions analysis
        CASE 
            WHEN ttw_kg IS NOT NULL AND wtt_kg IS NOT NULL
            THEN ttw_kg + wtt_kg
            ELSE co2e_kg
        END AS total_emissions_kg,
        
        -- Cost efficiency (placeholder for future cost data)
        CASE 
            WHEN distance_km > 0 AND payload_mass_kg > 0
            THEN 'efficient'
            ELSE 'inefficient'
        END AS efficiency_rating
        
    FROM cleaned
)

SELECT * FROM final