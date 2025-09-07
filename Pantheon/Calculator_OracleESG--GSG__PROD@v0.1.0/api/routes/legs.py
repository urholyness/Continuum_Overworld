from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

from models import get_db, Leg, Batch, TransportMode, DataQuality

router = APIRouter()

class LegCreate(BaseModel):
    mode: str = Field(..., example="truck")
    from_loc: str = Field(..., example="Eldoret")
    to_loc: str = Field(..., example="NBO")
    distance_km: float = Field(..., example=320)
    payload_t: float = Field(..., example=1.08)
    load_factor_pct: float = Field(70, example=70)
    backhaul: bool = Field(False, example=False)
    vehicle_class: str = Field(..., example="Rigid_7.5-12t_Euro6")
    energy_type: str = Field(None, example="diesel_l")
    energy_qty: float = Field(None)
    date: datetime = Field(None, example="2025-08-28")
    data_quality: str = Field("default", example="default")
    rf_apply: bool = Field(False, example=False)

class LegResponse(BaseModel):
    id: int
    batch_id: int
    mode: str
    from_loc: str
    to_loc: str
    distance_km: float
    payload_t: float
    load_factor_pct: float
    backhaul: bool
    vehicle_class: str
    energy_type: str
    data_quality: str
    rf_apply: bool
    
    class Config:
        from_attributes = True

@router.post("/{batch_id}/legs", response_model=List[LegResponse])
async def create_legs(
    batch_id: int,
    legs: List[LegCreate],
    db: Session = Depends(get_db)
):
    """Create multiple legs for a batch"""
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    created_legs = []
    for leg_data in legs:
        db_leg = Leg(
            batch_id=batch_id,
            mode=TransportMode[leg_data.mode.upper()],
            from_loc=leg_data.from_loc,
            to_loc=leg_data.to_loc,
            distance_km=leg_data.distance_km,
            payload_t=leg_data.payload_t,
            load_factor_pct=leg_data.load_factor_pct,
            backhaul=leg_data.backhaul,
            vehicle_class=leg_data.vehicle_class,
            energy_type=leg_data.energy_type,
            energy_qty=leg_data.energy_qty,
            date=leg_data.date,
            data_quality=DataQuality[leg_data.data_quality.upper()],
            rf_apply=leg_data.rf_apply
        )
        db.add(db_leg)
        created_legs.append(db_leg)
    
    db.commit()
    
    # Convert enum values to strings for response
    response_legs = []
    for leg in created_legs:
        response_legs.append({
            "id": leg.id,
            "batch_id": leg.batch_id,
            "mode": leg.mode.value,
            "from_loc": leg.from_loc,
            "to_loc": leg.to_loc,
            "distance_km": leg.distance_km,
            "payload_t": leg.payload_t,
            "load_factor_pct": leg.load_factor_pct,
            "backhaul": leg.backhaul,
            "vehicle_class": leg.vehicle_class,
            "energy_type": leg.energy_type,
            "data_quality": leg.data_quality.value,
            "rf_apply": leg.rf_apply
        })
    
    return response_legs

@router.get("/{batch_id}/legs", response_model=List[LegResponse])
async def get_batch_legs(batch_id: int, db: Session = Depends(get_db)):
    """Get all legs for a batch"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    response_legs = []
    for leg in batch.legs:
        response_legs.append({
            "id": leg.id,
            "batch_id": leg.batch_id,
            "mode": leg.mode.value,
            "from_loc": leg.from_loc,
            "to_loc": leg.to_loc,
            "distance_km": leg.distance_km,
            "payload_t": leg.payload_t,
            "load_factor_pct": leg.load_factor_pct,
            "backhaul": leg.backhaul,
            "vehicle_class": leg.vehicle_class,
            "energy_type": leg.energy_type,
            "data_quality": leg.data_quality.value,
            "rf_apply": leg.rf_apply
        })
    
    return response_legs

@router.delete("/{batch_id}/legs/{leg_id}")
async def delete_leg(batch_id: int, leg_id: int, db: Session = Depends(get_db)):
    """Delete a specific leg"""
    leg = db.query(Leg).filter(
        Leg.id == leg_id,
        Leg.batch_id == batch_id
    ).first()
    
    if not leg:
        raise HTTPException(status_code=404, detail="Leg not found")
    
    db.delete(leg)
    db.commit()
    
    return {"message": "Leg deleted successfully"}