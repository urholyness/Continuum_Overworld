"""
Unit tests for truck transport calculations
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Batch, Leg, TransportMode, DataQuality, Factor
from calc.iso14083 import ISO14083Calculator

# Test database setup
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Add test factors
    factor = Factor(
        pack_id="TEST-PACK",
        mode="truck",
        vehicle_class="Rigid_7.5-12t_Euro6",
        unit="kgCO2e/t.km",
        co2e_per_unit=0.1876,
        ttw_share=0.72,
        wtt_share=0.28,
        table_ref="Test table"
    )
    db.add(factor)
    db.commit()
    
    yield db
    db.close()

def test_truck_calculation_basic(test_db):
    """Test basic truck emission calculation"""
    
    # Create test batch
    batch = Batch(
        commodity="Test goods",
        net_mass_kg=1000,
        pkg_mass_kg=80,
        ownership="3PL"
    )
    test_db.add(batch)
    test_db.commit()
    
    # Add truck leg
    leg = Leg(
        batch_id=batch.id,
        mode=TransportMode.TRUCK,
        from_loc="Origin",
        to_loc="Destination",
        distance_km=320,
        payload_t=1.08,
        vehicle_class="Rigid_7.5-12t_Euro6",
        data_quality=DataQuality.DEFAULT
    )
    test_db.add(leg)
    test_db.commit()
    
    # Calculate
    calculator = ISO14083Calculator(test_db, "TEST-PACK")
    result = calculator.calculate_batch(batch)
    
    # Verify calculations
    assert len(result["legs"]) == 1
    leg_result = result["legs"][0]
    
    # Expected: 320 km * 1.08 t * 0.1876 kgCO2e/t.km = 64.84 kg
    expected_total = 320 * 1.08 * 0.1876
    assert abs(leg_result["total_kg"] - expected_total) < 0.1
    
    # Check TTW/WTT split (72/28)
    expected_ttw = expected_total * 0.72
    expected_wtt = expected_total * 0.28
    assert abs(leg_result["ttw_kg"] - expected_ttw) < 0.1
    assert abs(leg_result["wtt_kg"] - expected_wtt) < 0.1

def test_truck_with_load_factor(test_db):
    """Test truck calculation with load factor adjustment"""
    
    batch = Batch(
        commodity="Test goods",
        net_mass_kg=1000,
        pkg_mass_kg=80,
        ownership="3PL"
    )
    test_db.add(batch)
    test_db.commit()
    
    # Add truck leg with 70% load factor
    leg = Leg(
        batch_id=batch.id,
        mode=TransportMode.TRUCK,
        from_loc="Origin",
        to_loc="Destination",
        distance_km=100,
        payload_t=1.0,
        load_factor_pct=70,  # 70% loaded
        vehicle_class="Rigid_7.5-12t_Euro6",
        data_quality=DataQuality.DEFAULT
    )
    test_db.add(leg)
    test_db.commit()
    
    calculator = ISO14083Calculator(test_db, "TEST-PACK")
    result = calculator.calculate_batch(batch)
    
    leg_result = result["legs"][0]
    
    # With 70% load factor, emissions should be higher
    # Activity = 100 * 1.0 / 0.7 = 142.86 t.km
    expected_total = (100 * 1.0 / 0.7) * 0.1876
    assert abs(leg_result["total_kg"] - expected_total) < 0.1

def test_truck_backhaul(test_db):
    """Test truck calculation with backhaul optimization"""
    
    batch = Batch(
        commodity="Test goods",
        net_mass_kg=1000,
        pkg_mass_kg=80,
        ownership="3PL"
    )
    test_db.add(batch)
    test_db.commit()
    
    # Add backhaul leg
    leg = Leg(
        batch_id=batch.id,
        mode=TransportMode.TRUCK,
        from_loc="Origin",
        to_loc="Destination",
        distance_km=200,
        payload_t=1.0,
        backhaul=True,  # Backhaul trip
        vehicle_class="Rigid_7.5-12t_Euro6",
        data_quality=DataQuality.DEFAULT
    )
    test_db.add(leg)
    test_db.commit()
    
    calculator = ISO14083Calculator(test_db, "TEST-PACK")
    result = calculator.calculate_batch(batch)
    
    leg_result = result["legs"][0]
    
    # Backhaul gets 50% allocation
    base_emissions = 200 * 1.0 * 0.1876
    expected_total = base_emissions * 0.5
    assert abs(leg_result["total_kg"] - expected_total) < 0.1
    assert leg_result["backhaul"] is True