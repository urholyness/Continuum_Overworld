"""
DEFRA 2024 Emission Factors Loader
Loads UK Government GHG Conversion Factors into database
"""

import pandas as pd
from sqlalchemy.orm import Session
from models import Factor, engine, SessionLocal, init_db
import os
import json

# Sample DEFRA 2024 factors (normally loaded from Excel)
DEFRA_2024_FACTORS = [
    # Road transport - Trucks
    {
        "mode": "truck",
        "vehicle_class": "Rigid_7.5-12t_Euro6",
        "unit": "kgCO2e/t.km",
        "co2e_per_unit": 0.1876,
        "ttw_share": 0.72,
        "wtt_share": 0.28,
        "table_ref": "Freighting goods - HGVs - All diesel",
        "notes": "Average laden, Euro 6"
    },
    {
        "mode": "truck",
        "vehicle_class": "Articulated_>33t_Euro6",
        "unit": "kgCO2e/t.km",
        "co2e_per_unit": 0.0584,
        "ttw_share": 0.72,
        "wtt_share": 0.28,
        "table_ref": "Freighting goods - HGVs - All diesel",
        "notes": "Average laden, Euro 6"
    },
    
    # Air freight
    {
        "mode": "air",
        "vehicle_class": "Widebody_Freighter",
        "unit": "kgCO2e/t.km",
        "co2e_per_unit": 0.8983,
        "ttw_share": 0.85,
        "wtt_share": 0.15,
        "rf_uplift": 1.9,  # Radiative Forcing multiplier
        "table_ref": "Freighting goods - Air - Long-haul international",
        "notes": "With RF uplift available"
    },
    {
        "mode": "air",
        "vehicle_class": "Narrowbody_Freighter",
        "unit": "kgCO2e/t.km",
        "co2e_per_unit": 1.2345,
        "ttw_share": 0.85,
        "wtt_share": 0.15,
        "rf_uplift": 1.9,
        "table_ref": "Freighting goods - Air - Short-haul",
        "notes": "With RF uplift available"
    },
    
    # Rail freight
    {
        "mode": "rail",
        "vehicle_class": "EU_Freight_Rail_Avg",
        "unit": "kgCO2e/t.km",
        "co2e_per_unit": 0.0275,
        "ttw_share": 0.65,
        "wtt_share": 0.35,
        "table_ref": "Freighting goods - Rail",
        "notes": "EU average electric/diesel mix"
    },
    {
        "mode": "rail",
        "vehicle_class": "UK_Freight_Rail",
        "unit": "kgCO2e/t.km",
        "co2e_per_unit": 0.0289,
        "ttw_share": 0.60,
        "wtt_share": 0.40,
        "table_ref": "Freighting goods - Rail",
        "notes": "UK rail freight"
    },
    
    # Sea freight
    {
        "mode": "ship",
        "vehicle_class": "Container_Ship_Large",
        "unit": "kgCO2e/t.km",
        "co2e_per_unit": 0.0089,
        "ttw_share": 0.87,
        "wtt_share": 0.13,
        "table_ref": "Freighting goods - Sea - Container ship",
        "notes": "Large container vessel >8000 TEU"
    },
    {
        "mode": "ship",
        "vehicle_class": "RoRo_Ferry",
        "unit": "kgCO2e/t.km",
        "co2e_per_unit": 0.0456,
        "ttw_share": 0.87,
        "wtt_share": 0.13,
        "table_ref": "Freighting goods - Sea - RoRo ferry",
        "notes": "Roll-on/Roll-off ferry"
    },
    
    # Electricity factors
    {
        "mode": "electricity",
        "vehicle_class": "grid_average",
        "unit": "kgCO2e/kWh",
        "co2e_per_unit": 0.2074,  # UK grid average 2024
        "ttw_share": 1.0,
        "wtt_share": 0,
        "table_ref": "UK electricity - Grid average",
        "notes": "Location-based method"
    },
    {
        "mode": "electricity",
        "vehicle_class": "diesel_generator",
        "unit": "kgCO2e/kWh",
        "co2e_per_unit": 0.7341,
        "ttw_share": 0.85,
        "wtt_share": 0.15,
        "table_ref": "Stationary combustion - Diesel generator",
        "notes": "Small/medium generator"
    }
]

def load_defra_factors(db: Session = None):
    """Load DEFRA 2024 emission factors into database"""
    
    if db is None:
        db = SessionLocal()
    
    try:
        # Clear existing DEFRA-2024 factors
        db.query(Factor).filter(Factor.pack_id == "DEFRA-2024").delete()
        
        # Load new factors
        for factor_data in DEFRA_2024_FACTORS:
            factor = Factor(
                pack_id="DEFRA-2024",
                source_url="https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
                version="2024.1",
                region="UK/EU",
                **factor_data
            )
            db.add(factor)
        
        db.commit()
        print(f"Loaded {len(DEFRA_2024_FACTORS)} DEFRA 2024 emission factors")
        
        # Create factors metadata file
        metadata = {
            "pack_id": "DEFRA-2024",
            "version": "2024.1",
            "source": "UK Government GHG Conversion Factors 2024",
            "url": "https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
            "loaded_factors": len(DEFRA_2024_FACTORS),
            "modes": list(set(f["mode"] for f in DEFRA_2024_FACTORS)),
            "notes": "Simplified subset for MVP. Full dataset available in Excel format."
        }
        
        # Save metadata
        data_dir = os.path.dirname(os.path.abspath(__file__))
        metadata_path = os.path.join(data_dir, "data", "factors", "DEFRA_2024_metadata.json")
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Metadata saved to {metadata_path}")
        
    except Exception as e:
        db.rollback()
        print(f"Error loading factors: {e}")
        raise
    finally:
        if db:
            db.close()

def init_database_with_factors():
    """Initialize database and load default factors"""
    print("Initializing database...")
    init_db()
    
    print("Loading DEFRA 2024 factors...")
    load_defra_factors()
    
    print("Database initialization complete!")

if __name__ == "__main__":
    init_database_with_factors()