"""
GLEC Framework v3.0 (2024) implementation
Smart Freight Centre's Global Logistics Emissions Council methodology
"""

from typing import Dict, List
from models import Batch, TransportMode
from collections import defaultdict

class GLECCalculator:
    def __init__(self):
        self.mode_categories = {
            TransportMode.TRUCK: "road",
            TransportMode.RAIL: "rail",
            TransportMode.SHIP: "sea",
            TransportMode.AIR: "air",
            TransportMode.BARGE: "inland_waterway"
        }
    
    def calculate_glec_summary(self, batch: Batch, iso_results: Dict) -> Dict:
        """
        Generate GLEC-compliant summary from ISO 14083 results
        Groups by transport mode and provides allocation insights
        """
        
        glec_summary = {
            "framework": "GLEC v3.0",
            "modes": defaultdict(lambda: {
                "legs": 0,
                "total_distance_km": 0,
                "total_payload_t": 0,
                "total_emissions_kg": 0,
                "ttw_kg": 0,
                "wtt_kg": 0,
                "avg_load_factor": 0,
                "allocation_method": "mass_distance"
            }),
            "hubs": {
                "total_kwh": 0,
                "total_emissions_kg": 0,
                "renewable_kwh": 0,
                "grid_kwh": 0
            },
            "allocation": {
                "method": "mass_distance",
                "basis": "payload_tonnes",
                "load_factors_applied": True
            }
        }
        
        # Process transport legs
        for leg_result in iso_results.get("legs", []):
            # Find matching leg from batch
            leg = next((l for l in batch.legs if l.id == leg_result["leg_id"]), None)
            if not leg:
                continue
            
            mode_category = self.mode_categories.get(leg.mode, "other")
            mode_summary = glec_summary["modes"][mode_category]
            
            mode_summary["legs"] += 1
            mode_summary["total_distance_km"] += leg.distance_km
            mode_summary["total_payload_t"] += leg.payload_t
            mode_summary["total_emissions_kg"] += leg_result["total_kg"]
            mode_summary["ttw_kg"] += leg_result["ttw_kg"]
            mode_summary["wtt_kg"] += leg_result["wtt_kg"]
            
            # Update average load factor
            if leg.load_factor_pct:
                current_avg = mode_summary["avg_load_factor"]
                mode_summary["avg_load_factor"] = (
                    (current_avg * (mode_summary["legs"] - 1) + leg.load_factor_pct) 
                    / mode_summary["legs"]
                )
            
            # Special handling for air freight
            if leg.mode == TransportMode.AIR:
                mode_summary["rf_applied"] = leg_result.get("rf_applied", False)
            
            # Note backhaul optimization
            if leg_result.get("backhaul"):
                mode_summary["backhaul_optimized"] = True
        
        # Process hub activities
        for hub in batch.hubs:
            hub_result = next(
                (h for h in iso_results.get("hubs", []) if h["hub_id"] == hub.id), 
                None
            )
            if hub_result:
                glec_summary["hubs"]["total_kwh"] += hub.kwh
                glec_summary["hubs"]["total_emissions_kg"] += hub_result["total_kg"]
                
                if hub.energy_source.value in ["solar", "wind"]:
                    glec_summary["hubs"]["renewable_kwh"] += hub.kwh
                else:
                    glec_summary["hubs"]["grid_kwh"] += hub.kwh
        
        # Calculate renewable percentage
        if glec_summary["hubs"]["total_kwh"] > 0:
            glec_summary["hubs"]["renewable_pct"] = round(
                (glec_summary["hubs"]["renewable_kwh"] / glec_summary["hubs"]["total_kwh"]) * 100,
                1
            )
        
        # Convert defaultdict to regular dict for JSON serialization
        glec_summary["modes"] = dict(glec_summary["modes"])
        
        # Add efficiency metrics
        for mode, data in glec_summary["modes"].items():
            if data["total_distance_km"] > 0 and data["total_payload_t"] > 0:
                # Calculate emissions intensity (g CO2e/t.km)
                data["emissions_intensity_g_per_tkm"] = round(
                    (data["total_emissions_kg"] * 1000) / 
                    (data["total_distance_km"] * data["total_payload_t"]),
                    2
                )
        
        return glec_summary
    
    def get_allocation_guidance(self, ownership: str) -> Dict:
        """
        Provide GLEC allocation guidance based on ownership model
        """
        if ownership == "own":
            return {
                "allocation": "full",
                "guidance": "As owner-operator, full emissions allocated to scope 1/3",
                "verification": "Primary data from own fleet recommended"
            }
        elif ownership == "3PL":
            return {
                "allocation": "service_based",
                "guidance": "Third-party logistics emissions allocated to scope 3 cat 4/9",
                "verification": "Request carrier-specific factors where available"
            }
        else:
            return {
                "allocation": "default",
                "guidance": "Apply standard mass-distance allocation",
                "verification": "Use GLEC default factors"
            }