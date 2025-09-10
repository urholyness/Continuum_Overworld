"""
Unit tests for air freight calculations with Radiative Forcing
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Batch, Leg, TransportMode, DataQuality, Factor
from calc.iso14083 import ISO14083Calculator

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Add air freight factor with RF uplift
    factor = Factor(
        pack_id="TEST-PACK",
        mode="air",
        vehicle_class="Widebody_Freighter",
        unit="kgCO2e/t.km",
        co2e_per_unit=0.8983,
        ttw_share=0.85,
        wtt_share=0.15,
        rf_uplift=1.9,  # DEFRA standard RF multiplier
        table_ref="Air freight - long haul"
    )
    db.add(factor)
    db.commit()
    
    yield db
    db.close()

def test_air_freight_without_rf(test_db):
    """Test air freight calculation without RF uplift"""
    
    batch = Batch(
        commodity="High-value goods",
        net_mass_kg=500,
        pkg_mass_kg=50,
        ownership="3PL"
    )
    test_db.add(batch)
    test_db.commit()
    
    # Add air leg without RF
    leg = Leg(
        batch_id=batch.id,
        mode=TransportMode.AIR,
        from_loc="NBO",
        to_loc="FRA",
        distance_km=6200,
        payload_t=0.55,
        vehicle_class="Widebody_Freighter",
        rf_apply=False,  # No RF uplift
        data_quality=DataQuality.DEFAULT
    )
    test_db.add(leg)
    test_db.commit()
    
    calculator = ISO14083Calculator(test_db, "TEST-PACK")
    result = calculator.calculate_batch(batch, rf_apply=True)  # Global RF enabled
    
    leg_result = result["legs"][0]
    
    # Without RF: 6200 km * 0.55 t * 0.8983 kgCO2e/t.km
    expected_total = 6200 * 0.55 * 0.8983
    assert abs(leg_result["total_kg"] - expected_total) < 1
    assert leg_result["rf_applied"] is False

def test_air_freight_with_rf(test_db):
    """Test air freight calculation with RF uplift"""
    
    batch = Batch(
        commodity="High-value goods",
        net_mass_kg=500,
        pkg_mass_kg=50,
        ownership="3PL"
    )
    test_db.add(batch)
    test_db.commit()
    
    # Add air leg with RF
    leg = Leg(
        batch_id=batch.id,
        mode=TransportMode.AIR,
        from_loc="NBO",
        to_loc="FRA",
        distance_km=6200,
        payload_t=0.55,
        vehicle_class="Widebody_Freighter",
        rf_apply=True,  # Apply RF uplift
        data_quality=DataQuality.DEFAULT
    )
    test_db.add(leg)
    test_db.commit()
    
    calculator = ISO14083Calculator(test_db, "TEST-PACK")
    result = calculator.calculate_batch(batch, rf_apply=True)
    
    leg_result = result["legs"][0]
    
    # With RF: base emissions * 1.9
    base_emissions = 6200 * 0.55 * 0.8983
    expected_total = base_emissions * 1.9
    assert abs(leg_result["total_kg"] - expected_total) < 1
    assert leg_result["rf_applied"] is True

def test_air_freight_ttw_wtt_split_with_rf(test_db):
    """Test that RF is applied to both TTW and WTT components"""
    
    batch = Batch(
        commodity="Test goods",
        net_mass_kg=1000,
        pkg_mass_kg=100,
        ownership="3PL"
    )
    test_db.add(batch)
    test_db.commit()
    
    leg = Leg(
        batch_id=batch.id,
        mode=TransportMode.AIR,
        from_loc="LHR",
        to_loc="JFK",
        distance_km=5500,
        payload_t=1.1,
        vehicle_class="Widebody_Freighter",
        rf_apply=True,
        data_quality=DataQuality.DEFAULT
    )
    test_db.add(leg)
    test_db.commit()
    
    calculator = ISO14083Calculator(test_db, "TEST-PACK")
    result = calculator.calculate_batch(batch, rf_apply=True)
    
    leg_result = result["legs"][0]
    
    # Calculate expected values
    base_emissions = 5500 * 1.1 * 0.8983
    base_ttw = base_emissions * 0.85
    base_wtt = base_emissions * 0.15
    
    # Both should be multiplied by RF
    expected_ttw = base_ttw * 1.9
    expected_wtt = base_wtt * 1.9
    
    assert abs(leg_result["ttw_kg"] - expected_ttw) < 1
    assert abs(leg_result["wtt_kg"] - expected_wtt) < 1
    assert abs(leg_result["total_kg"] - (expected_ttw + expected_wtt)) < 1

def test_mixed_transport_with_air_rf(test_db):
    """Test mixed transport modes with selective RF application"""
    
    # Add truck factor
    truck_factor = Factor(
        pack_id="TEST-PACK",
        mode="truck",
        vehicle_class="Rigid_7.5-12t_Euro6",
        unit="kgCO2e/t.km",
        co2e_per_unit=0.1876,
        ttw_share=0.72,
        wtt_share=0.28,
        table_ref="Truck transport"
    )
    test_db.add(truck_factor)
    test_db.commit()
    
    batch = Batch(
        commodity="Mixed transport goods",
        net_mass_kg=1000,
        pkg_mass_kg=80,
        ownership="3PL"
    )
    test_db.add(batch)
    test_db.commit()
    
    # Add truck leg
    truck_leg = Leg(
        batch_id=batch.id,
        mode=TransportMode.TRUCK,
        from_loc="Farm",
        to_loc="Airport",
        distance_km=100,
        payload_t=1.08,
        vehicle_class="Rigid_7.5-12t_Euro6",
        data_quality=DataQuality.DEFAULT
    )
    test_db.add(truck_leg)
    
    # Add air leg with RF
    air_leg = Leg(
        batch_id=batch.id,
        mode=TransportMode.AIR,
        from_loc="Airport",
        to_loc="Destination",
        distance_km=3000,
        payload_t=1.08,
        vehicle_class="Widebody_Freighter",
        rf_apply=True,
        data_quality=DataQuality.DEFAULT
    )
    test_db.add(air_leg)
    test_db.commit()
    
    calculator = ISO14083Calculator(test_db, "TEST-PACK")
    result = calculator.calculate_batch(batch, rf_apply=True)
    
    assert len(result["legs"]) == 2
    
    # Truck should not have RF
    truck_result = next(r for r in result["legs"] if r["mode"] == "truck")
    assert "rf_applied" not in truck_result or truck_result["rf_applied"] is False
    
    # Air should have RF
    air_result = next(r for r in result["legs"] if r["mode"] == "air")
    assert air_result["rf_applied"] is True
    
    # Verify air emissions are higher due to RF
    base_air_emissions = 3000 * 1.08 * 0.8983
    assert air_result["total_kg"] > base_air_emissions * 1.8  # Should be ~1.9x