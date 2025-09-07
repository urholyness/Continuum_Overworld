{{ config(materialized='table') }}

WITH route_emissions AS (
    SELECT 
        tenant_id,
        project_tag,
        commodity,
        hs_code,
        transport_category,
        mode,
        from_location,
        to_location,
        from_code,
        to_code,
        SUM(payload_mass_kg) AS total_payload_kg,
        SUM(co2e_kg) AS total_emissions_kg,
        AVG(emissions_intensity_kg_co2e_per_tkm) AS avg_emissions_intensity,
        SUM(distance_km) AS total_distance_km,
        COUNT(*) AS shipment_count,
        AVG(load_factor_pct) AS avg_load_factor,
        AVG(duration_hours) AS avg_duration_hours,
        
        -- Performance metrics
        AVG(departure_delay_hours) AS avg_departure_delay,
        AVG(arrival_delay_hours) AS avg_arrival_delay,
        
        -- Cost efficiency (placeholder for future cost data)
        AVG(efficiency_rating) AS avg_efficiency_rating
        
    FROM {{ ref('silver_fct_emissions') }}
    WHERE data_quality_status = 'valid'
    GROUP BY 
        tenant_id, project_tag, commodity, hs_code, transport_category, 
        mode, from_location, to_location, from_code, to_code
),

route_rankings AS (
    SELECT 
        *,
        
        -- Route efficiency score (0-100)
        CASE 
            WHEN avg_emissions_intensity <= 0.05 THEN 100
            WHEN avg_emissions_intensity <= 0.10 THEN 90
            WHEN avg_emissions_intensity <= 0.20 THEN 80
            WHEN avg_emissions_intensity <= 0.50 THEN 70
            WHEN avg_emissions_intensity <= 1.00 THEN 60
            WHEN avg_emissions_intensity <= 2.00 THEN 50
            WHEN avg_emissions_intensity <= 5.00 THEN 40
            ELSE 30
        END AS efficiency_score,
        
        -- Load factor score (0-100)
        CASE 
            WHEN avg_load_factor >= 90 THEN 100
            WHEN avg_load_factor >= 80 THEN 90
            WHEN avg_load_factor >= 70 THEN 80
            WHEN avg_load_factor >= 60 THEN 70
            WHEN avg_load_factor >= 50 THEN 60
            WHEN avg_load_factor >= 40 THEN 50
            WHEN avg_load_factor >= 30 THEN 40
            WHEN avg_load_factor >= 20 THEN 30
            ELSE 20
        END AS load_factor_score,
        
        -- Reliability score (0-100)
        CASE 
            WHEN avg_departure_delay <= 0.5 AND avg_arrival_delay <= 0.5 THEN 100
            WHEN avg_departure_delay <= 1.0 AND avg_arrival_delay <= 1.0 THEN 90
            WHEN avg_departure_delay <= 2.0 AND avg_arrival_delay <= 2.0 THEN 80
            WHEN avg_departure_delay <= 4.0 AND avg_arrival_delay <= 4.0 THEN 70
            WHEN avg_departure_delay <= 8.0 AND avg_arrival_delay <= 8.0 THEN 60
            ELSE 50
        END AS reliability_score,
        
        -- Overall route score (weighted average)
        (
            (efficiency_score * 0.4) + 
            (load_factor_score * 0.3) + 
            (reliability_score * 0.3)
        ) AS overall_route_score
        
    FROM route_emissions
),

final_summary AS (
    SELECT
        tenant_id,
        project_tag,
        commodity,
        hs_code,
        transport_category,
        mode,
        from_location,
        to_location,
        from_code,
        to_code,
        
        -- Volume metrics
        total_payload_kg,
        total_emissions_kg,
        total_distance_km,
        shipment_count,
        
        -- Performance metrics
        avg_emissions_intensity,
        avg_load_factor,
        avg_duration_hours,
        avg_departure_delay,
        avg_arrival_delay,
        avg_efficiency_rating,
        
        -- Scoring
        efficiency_score,
        load_factor_score,
        reliability_score,
        overall_route_score,
        
        -- Route classification
        CASE 
            WHEN overall_route_score >= 90 THEN 'excellent'
            WHEN overall_route_score >= 80 THEN 'very_good'
            WHEN overall_route_score >= 70 THEN 'good'
            WHEN overall_route_score >= 60 THEN 'fair'
            WHEN overall_route_score >= 50 THEN 'poor'
            ELSE 'very_poor'
        END AS route_quality_rating,
        
        -- Optimization opportunities
        CASE 
            WHEN efficiency_score < 70 THEN 'High emissions - optimize route or mode'
            WHEN load_factor_score < 70 THEN 'Low utilization - improve load planning'
            WHEN reliability_score < 70 THEN 'Poor reliability - investigate delays'
            WHEN overall_route_score < 70 THEN 'Multiple issues - comprehensive review needed'
            ELSE 'Route performing well - monitor for degradation'
        END AS optimization_opportunity,
        
        -- Priority for improvement
        CASE 
            WHEN overall_route_score < 50 THEN 'Critical - immediate attention required'
            WHEN overall_route_score < 60 THEN 'High - schedule improvement planning'
            WHEN overall_route_score < 70 THEN 'Medium - include in next quarter review'
            WHEN overall_route_score < 80 THEN 'Low - monitor and maintain'
            ELSE 'Excellent - no action required'
        END AS improvement_priority,
        
        -- Carbon footprint impact
        CASE 
            WHEN total_emissions_kg > 1000000 THEN 'Very High - major carbon impact'
            WHEN total_emissions_kg > 100000 THEN 'High - significant carbon impact'
            WHEN total_emissions_kg > 10000 THEN 'Medium - moderate carbon impact'
            WHEN total_emissions_kg > 1000 THEN 'Low - minor carbon impact'
            ELSE 'Very Low - minimal carbon impact'
        END AS carbon_impact_level,
        
        -- Route maturity
        CASE 
            WHEN shipment_count >= 100 THEN 'Mature - well-established route'
            WHEN shipment_count >= 50 THEN 'Developing - growing route'
            WHEN shipment_count >= 20 THEN 'Emerging - new route'
            WHEN shipment_count >= 10 THEN 'Pilot - testing route'
            ELSE 'Experimental - very new route'
        END AS route_maturity,
        
        CURRENT_TIMESTAMP AS summary_generated_at
        
    FROM route_rankings
)

SELECT * FROM final_summary
ORDER BY 
    tenant_id, 
    overall_route_score DESC, 
    total_emissions_kg DESC