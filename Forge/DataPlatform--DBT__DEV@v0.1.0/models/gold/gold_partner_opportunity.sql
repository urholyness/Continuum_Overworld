{{ config(materialized='table') }}

WITH esg_metrics AS (
    SELECT 
        tenant_id,
        org_id,
        metric_type,
        metric_category,
        metric_value_kg_co2e,
        confidence,
        occurred_at,
        data_quality_status
    FROM {{ ref('silver_fct_esg_metric') }}
    WHERE data_quality_status = 'valid'
),

emissions_summary AS (
    SELECT 
        tenant_id,
        commodity,
        transport_category,
        SUM(co2e_kg) AS total_emissions_kg,
        AVG(emissions_intensity_kg_co2e_per_tkm) AS avg_emissions_intensity,
        COUNT(*) AS shipment_count,
        AVG(distance_km) AS avg_distance_km
    FROM {{ ref('silver_fct_emissions') }}
    WHERE data_quality_status = 'valid'
    GROUP BY tenant_id, commodity, transport_category
),

agent_insights AS (
    SELECT 
        tenant_id,
        agent_name,
        agent_category,
        COUNT(*) AS run_count,
        AVG(success_indicator) AS success_rate,
        AVG(duration_seconds) AS avg_duration_seconds,
        SUM(cost_usd) AS total_cost_usd,
        AVG(memory_ops_per_second) AS avg_memory_intensity
    FROM {{ ref('silver_fct_agent_run') }}
    WHERE data_quality_status = 'valid'
    GROUP BY tenant_id, agent_name, agent_category
),

opportunity_signals AS (
    SELECT
        e.tenant_id,
        e.org_id,
        e.metric_type,
        e.metric_category,
        
        -- ESG Performance Signals
        CASE 
            WHEN e.metric_category = 'emissions' AND e.metric_value_kg_co2e > 1000000 THEN 'high_impact'
            WHEN e.metric_category = 'emissions' AND e.metric_value_kg_co2e > 100000 THEN 'medium_impact'
            WHEN e.metric_category = 'emissions' AND e.metric_value_kg_co2e > 10000 THEN 'low_impact'
            ELSE 'minimal_impact'
        END AS esg_impact_level,
        
        -- Confidence Quality
        CASE 
            WHEN e.confidence >= 0.9 THEN 'high_confidence'
            WHEN e.confidence >= 0.7 THEN 'medium_confidence'
            WHEN e.confidence >= 0.5 THEN 'low_confidence'
            ELSE 'very_low_confidence'
        END AS data_confidence_level,
        
        -- Recent Activity
        CASE 
            WHEN e.occurred_at >= CURRENT_DATE - INTERVAL '30 days' THEN 'recent'
            WHEN e.occurred_at >= CURRENT_DATE - INTERVAL '90 days' THEN 'recent_quarter'
            WHEN e.occurred_at >= CURRENT_DATE - INTERVAL '365 days' THEN 'recent_year'
            ELSE 'historical'
        END AS data_freshness,
        
        -- Opportunity Score (0-100)
        (
            CASE WHEN e.confidence >= 0.9 THEN 25 ELSE 0 END +
            CASE WHEN e.occurred_at >= CURRENT_DATE - INTERVAL '90 days' THEN 25 ELSE 0 END +
            CASE WHEN e.metric_value_kg_co2e > 100000 THEN 25 ELSE 0 END +
            CASE WHEN e.data_quality_status = 'valid' THEN 25 ELSE 0 END
        ) AS opportunity_score
        
    FROM esg_metrics e
),

final_opportunities AS (
    SELECT
        o.tenant_id,
        o.org_id,
        o.metric_type,
        o.metric_category,
        o.esg_impact_level,
        o.data_confidence_level,
        o.data_freshness,
        o.opportunity_score,
        
        -- Partner Opportunity Type
        CASE 
            WHEN o.metric_category = 'emissions' AND o.esg_impact_level IN ('high_impact', 'medium_impact') 
            THEN 'emissions_reduction_partner'
            WHEN o.metric_category = 'water' AND o.opportunity_score >= 75 
            THEN 'water_efficiency_partner'
            WHEN o.metric_category = 'waste' AND o.opportunity_score >= 75 
            THEN 'waste_management_partner'
            WHEN o.metric_category = 'energy' AND o.opportunity_score >= 75 
            THEN 'energy_efficiency_partner'
            ELSE 'general_sustainability_partner'
        END AS partner_opportunity_type,
        
        -- Priority Level
        CASE 
            WHEN o.opportunity_score >= 90 THEN 'critical'
            WHEN o.opportunity_score >= 75 THEN 'high'
            WHEN o.opportunity_score >= 50 THEN 'medium'
            ELSE 'low'
        END AS priority_level,
        
        -- Suggested Actions
        CASE 
            WHEN o.metric_category = 'emissions' THEN 
                CASE 
                    WHEN o.esg_impact_level = 'high_impact' THEN 'Immediate emissions audit and reduction strategy required'
                    WHEN o.esg_impact_level = 'medium_impact' THEN 'Emissions monitoring and optimization program recommended'
                    ELSE 'Baseline emissions tracking and improvement opportunities'
                END
            WHEN o.metric_category = 'water' THEN 'Water efficiency assessment and conservation partnership'
            WHEN o.metric_category = 'waste' THEN 'Waste reduction and circular economy collaboration'
            WHEN o.metric_category = 'energy' THEN 'Energy efficiency audit and renewable energy partnership'
            ELSE 'General sustainability assessment and improvement partnership'
        END AS suggested_actions,
        
        -- Next Steps
        CASE 
            WHEN o.priority_level = 'critical' THEN 'Schedule immediate partner meeting within 1 week'
            WHEN o.priority_level = 'high' THEN 'Schedule partner meeting within 2 weeks'
            WHEN o.priority_level = 'medium' THEN 'Schedule partner meeting within 1 month'
            ELSE 'Add to quarterly partner review cycle'
        END AS next_steps,
        
        -- Risk Assessment
        CASE 
            WHEN o.data_confidence_level = 'very_low_confidence' THEN 'High - data quality issues'
            WHEN o.data_confidence_level = 'low_confidence' THEN 'Medium - limited data reliability'
            WHEN o.data_confidence_level = 'medium_confidence' THEN 'Low - moderate data reliability'
            ELSE 'Very Low - high data reliability'
        END AS risk_assessment,
        
        CURRENT_TIMESTAMP AS opportunity_identified_at
        
    FROM opportunity_signals o
)

SELECT * FROM final_opportunities
ORDER BY opportunity_score DESC, priority_level, tenant_id