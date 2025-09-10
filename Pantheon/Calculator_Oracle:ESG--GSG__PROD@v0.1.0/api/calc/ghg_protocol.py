"""
GHG Protocol Scope 3 Standard implementation
Categories 4 (Upstream transportation) and 9 (Downstream transportation)
"""

from typing import Dict
from models import Batch

class GHGProtocolMapper:
    def __init__(self):
        self.scope_definitions = {
            "scope1": "Direct emissions from owned/controlled sources",
            "scope2": "Indirect emissions from purchased electricity",
            "scope3": "Other indirect emissions in value chain"
        }
        
        self.category_definitions = {
            "4": "Upstream transportation and distribution",
            "9": "Downstream transportation and distribution"
        }
    
    def map_to_scopes(self, batch: Batch, iso_results: Dict, glec_results: Dict) -> Dict:
        """
        Map emissions to GHG Protocol scopes and categories
        Based on ownership and point in supply chain
        """
        
        scopes = {
            "protocol": "GHG Protocol Corporate Standard",
            "scope1": {
                "description": self.scope_definitions["scope1"],
                "emissions_tco2e": 0,
                "sources": []
            },
            "scope2": {
                "description": self.scope_definitions["scope2"],
                "emissions_tco2e": 0,
                "sources": []
            },
            "scope3": {
                "description": self.scope_definitions["scope3"],
                "emissions_tco2e": 0,
                "categories": {
                    "4": {
                        "name": self.category_definitions["4"],
                        "emissions_tco2e": 0,
                        "activities": []
                    },
                    "9": {
                        "name": self.category_definitions["9"],
                        "emissions_tco2e": 0,
                        "activities": []
                    }
                }
            },
            "total_tco2e": 0
        }
        
        # Process transport legs based on ownership
        for leg_result in iso_results.get("legs", []):
            leg = next((l for l in batch.legs if l.id == leg_result["leg_id"]), None)
            if not leg:
                continue
            
            emissions_t = leg_result["total_kg"] / 1000  # Convert kg to tonnes
            
            if batch.ownership == "own":
                # Own fleet = Scope 1
                scopes["scope1"]["emissions_tco2e"] += emissions_t
                scopes["scope1"]["sources"].append({
                    "type": f"{leg.mode.value}_transport",
                    "route": f"{leg.from_loc} → {leg.to_loc}",
                    "emissions_tco2e": round(emissions_t, 3)
                })
            else:
                # 3PL or purchased transport = Scope 3
                # Determine if upstream (Cat 4) or downstream (Cat 9)
                if self._is_upstream(leg.from_loc, leg.to_loc):
                    category = "4"
                else:
                    category = "9"
                
                scopes["scope3"]["categories"][category]["emissions_tco2e"] += emissions_t
                scopes["scope3"]["categories"][category]["activities"].append({
                    "mode": leg.mode.value,
                    "route": f"{leg.from_loc} → {leg.to_loc}",
                    "distance_km": leg.distance_km,
                    "emissions_tco2e": round(emissions_t, 3),
                    "carrier": leg.carrier_id or "third_party"
                })
        
        # Process hub emissions (primarily Scope 2 for purchased electricity)
        for hub_result in iso_results.get("hubs", []):
            hub = next((h for h in batch.hubs if h["hub_id"] == hub_result["hub_id"]), None)
            if not hub:
                continue
            
            emissions_t = hub_result["total_kg"] / 1000
            
            if hub.energy_source.value in ["grid"]:
                # Purchased electricity = Scope 2
                scopes["scope2"]["emissions_tco2e"] += emissions_t
                scopes["scope2"]["sources"].append({
                    "type": hub.type.value,
                    "energy": f"{hub.kwh} kWh",
                    "source": hub.energy_source.value,
                    "emissions_tco2e": round(emissions_t, 3)
                })
            elif hub.energy_source.value == "diesel":
                # Diesel generator = Scope 1 if owned
                if batch.ownership == "own":
                    scopes["scope1"]["emissions_tco2e"] += emissions_t
                    scopes["scope1"]["sources"].append({
                        "type": f"{hub.type.value}_diesel_gen",
                        "energy": f"{hub.kwh} kWh",
                        "emissions_tco2e": round(emissions_t, 3)
                    })
                else:
                    # Otherwise Scope 3
                    scopes["scope3"]["categories"]["4"]["emissions_tco2e"] += emissions_t
            elif hub.energy_source.value in ["solar", "wind"]:
                # Renewable energy - minimal emissions, could be Scope 2 or 3
                # Typically reported separately or in Scope 2 with renewable attributes
                scopes["scope2"]["emissions_tco2e"] += emissions_t
                scopes["scope2"]["sources"].append({
                    "type": hub.type.value,
                    "energy": f"{hub.kwh} kWh",
                    "source": f"renewable_{hub.energy_source.value}",
                    "emissions_tco2e": round(emissions_t, 3)
                })
        
        # Calculate totals
        scopes["scope3"]["emissions_tco2e"] = sum(
            cat["emissions_tco2e"] 
            for cat in scopes["scope3"]["categories"].values()
        )
        
        scopes["total_tco2e"] = round(
            scopes["scope1"]["emissions_tco2e"] +
            scopes["scope2"]["emissions_tco2e"] +
            scopes["scope3"]["emissions_tco2e"],
            3
        )
        
        # Add reporting guidance
        scopes["reporting_notes"] = self._get_reporting_notes(batch)
        
        return scopes
    
    def _is_upstream(self, from_loc: str, to_loc: str) -> bool:
        """
        Determine if transportation is upstream (before point of sale) or downstream
        Simplified logic - in practice would use more sophisticated supply chain mapping
        """
        # Define major ports/hubs that typically indicate downstream distribution
        downstream_indicators = ["Hamburg", "Rotterdam", "Antwerp", "EU", "US", "buyer"]
        
        # If destination contains downstream indicators, it's likely Category 9
        for indicator in downstream_indicators:
            if indicator.lower() in to_loc.lower():
                return False
        
        # Default to upstream (Category 4) for farm-to-port movements
        return True
    
    def _get_reporting_notes(self, batch: Batch) -> Dict:
        """
        Provide GHG Protocol reporting guidance
        """
        notes = {
            "boundary": "Cradle-to-customer for agricultural products",
            "allocation": "Mass-distance method per GLEC Framework",
            "data_quality": "Mix of primary and default factors"
        }
        
        if batch.ownership == "3PL":
            notes["ownership_model"] = "Third-party logistics - all transport in Scope 3"
        else:
            notes["ownership_model"] = "Owner-operator - own fleet in Scope 1"
        
        # Add CBAM relevance if flagged
        if batch.project and batch.project.cbam_flag:
            notes["cbam"] = "Embedded emissions calculated for CBAM compliance"
        
        return notes