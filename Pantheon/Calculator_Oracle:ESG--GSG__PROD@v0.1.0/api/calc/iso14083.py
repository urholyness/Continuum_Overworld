"""
ISO 14083:2023 compliant calculation engine
Implements TTW (Tank-to-Wheel) and WTT (Well-to-Tank) split
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models import Leg, Hub, Batch, Factor, TransportMode, EnergySource
import logging

logger = logging.getLogger(__name__)

class ISO14083Calculator:
    def __init__(self, db: Session, factor_pack: str = "DEFRA-2024"):
        self.db = db
        self.factor_pack = factor_pack
        
    def calculate_batch(self, batch: Batch, rf_apply: bool = True) -> Dict:
        """
        Calculate emissions for entire batch following ISO 14083 methodology
        Returns detailed breakdown with TTW/WTT split
        """
        results = {
            "batch_id": batch.id,
            "methodology": "ISO 14083:2023",
            "legs": [],
            "hubs": [],
            "totals": {
                "ttw_kg": 0,
                "wtt_kg": 0,
                "total_kg": 0,
                "intensity_kgco2e_per_kg": 0
            }
        }
        
        # Calculate emissions for each transport leg
        for leg in batch.legs:
            leg_emissions = self._calculate_leg(leg, rf_apply)
            results["legs"].append(leg_emissions)
            results["totals"]["ttw_kg"] += leg_emissions["ttw_kg"]
            results["totals"]["wtt_kg"] += leg_emissions["wtt_kg"]
            results["totals"]["total_kg"] += leg_emissions["total_kg"]
        
        # Calculate emissions for hubs (cold storage, packhouse)
        for hub in batch.hubs:
            hub_emissions = self._calculate_hub(hub)
            results["hubs"].append(hub_emissions)
            results["totals"]["total_kg"] += hub_emissions["total_kg"]
        
        # Calculate intensity per kg of product
        total_mass = batch.net_mass_kg + batch.pkg_mass_kg
        if total_mass > 0:
            results["totals"]["intensity_kgco2e_per_kg"] = results["totals"]["total_kg"] / total_mass
        
        return results
    
    def _calculate_leg(self, leg: Leg, rf_apply: bool) -> Dict:
        """Calculate emissions for a single transport leg"""
        
        # Get emission factor from database
        factor = self._get_factor(leg.mode, leg.vehicle_class)
        if not factor:
            logger.warning(f"No factor found for {leg.mode} - {leg.vehicle_class}")
            return {
                "leg_id": leg.id,
                "mode": leg.mode.value,
                "from": leg.from_loc,
                "to": leg.to_loc,
                "distance_km": leg.distance_km,
                "payload_t": leg.payload_t,
                "ttw_kg": 0,
                "wtt_kg": 0,
                "total_kg": 0,
                "factor_source": "not_found"
            }
        
        # Calculate activity data (tonne-kilometers)
        activity = leg.distance_km * leg.payload_t
        
        # Apply load factor adjustment if specified
        if leg.load_factor_pct and leg.load_factor_pct < 100:
            activity = activity / (leg.load_factor_pct / 100)
        
        # Calculate base emissions
        total_emissions = activity * factor.co2e_per_unit
        
        # Split into TTW and WTT
        ttw_share = factor.ttw_share if factor.ttw_share else 0.7  # Default 70% TTW
        wtt_share = factor.wtt_share if factor.wtt_share else 0.3  # Default 30% WTT
        
        ttw_kg = total_emissions * ttw_share
        wtt_kg = total_emissions * wtt_share
        
        # Apply Radiative Forcing for air freight if applicable
        if leg.mode == TransportMode.AIR and rf_apply and leg.rf_apply:
            rf_multiplier = factor.rf_uplift if factor.rf_uplift else 1.9  # DEFRA default
            ttw_kg *= rf_multiplier
            wtt_kg *= rf_multiplier
        
        # Adjust for backhaul if applicable
        if leg.backhaul:
            # Backhaul typically gets 50% allocation
            ttw_kg *= 0.5
            wtt_kg *= 0.5
        
        return {
            "leg_id": leg.id,
            "mode": leg.mode.value,
            "from": leg.from_loc,
            "to": leg.to_loc,
            "distance_km": leg.distance_km,
            "payload_t": leg.payload_t,
            "vehicle_class": leg.vehicle_class,
            "ttw_kg": round(ttw_kg, 2),
            "wtt_kg": round(wtt_kg, 2),
            "total_kg": round(ttw_kg + wtt_kg, 2),
            "factor_source": f"{factor.pack_id}:{factor.table_ref}",
            "rf_applied": leg.mode == TransportMode.AIR and rf_apply and leg.rf_apply,
            "backhaul": leg.backhaul
        }
    
    def _calculate_hub(self, hub: Hub) -> Dict:
        """Calculate emissions for hub activities (electricity usage)"""
        
        # Get electricity emission factor
        factor = self._get_electricity_factor(hub.energy_source)
        
        if hub.energy_source == EnergySource.SOLAR:
            # Solar has minimal operational emissions
            emissions_kg = hub.kwh * 0.01  # ~10g CO2e/kWh for solar PV lifecycle
        elif hub.energy_source == EnergySource.WIND:
            emissions_kg = hub.kwh * 0.012  # ~12g CO2e/kWh for wind
        else:
            # Grid or diesel generator
            emissions_kg = hub.kwh * (factor.co2e_per_unit if factor else 0.5)
        
        return {
            "hub_id": hub.id,
            "type": hub.type.value,
            "kwh": hub.kwh,
            "energy_source": hub.energy_source.value,
            "hours": hub.hours,
            "total_kg": round(emissions_kg, 2),
            "factor_source": f"{factor.pack_id}:{factor.table_ref}" if factor else "default"
        }
    
    def _get_factor(self, mode: TransportMode, vehicle_class: str) -> Optional[Factor]:
        """Retrieve emission factor from database"""
        return self.db.query(Factor).filter(
            Factor.pack_id == self.factor_pack,
            Factor.mode == mode.value,
            Factor.vehicle_class == vehicle_class
        ).first()
    
    def _get_electricity_factor(self, source: EnergySource) -> Optional[Factor]:
        """Retrieve electricity emission factor"""
        if source in [EnergySource.SOLAR, EnergySource.WIND]:
            # Renewable sources have minimal factors
            return None
        
        # Map energy source to factor lookup
        lookup_map = {
            EnergySource.GRID: "grid_average",
            EnergySource.DIESEL: "diesel_generator"
        }
        
        return self.db.query(Factor).filter(
            Factor.pack_id == self.factor_pack,
            Factor.mode == "electricity",
            Factor.vehicle_class == lookup_map.get(source, "grid_average")
        ).first()