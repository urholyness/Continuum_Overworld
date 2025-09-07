from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field

from models import get_db, Hub, Batch, HubType, EnergySource

router = APIRouter()

class HubCreate(BaseModel):
    type: str = Field(..., example="packhouse")
    kwh: float = Field(..., example=120)
    energy_source: str = Field(..., example="solar")
    hours: float = Field(24, example=24)
    location: str = Field(None, example="Eldoret")

class HubResponse(BaseModel):
    id: int
    batch_id: int
    type: str
    kwh: float
    energy_source: str
    hours: float
    location: str
    
    class Config:
        from_attributes = True

@router.post("/{batch_id}/hubs", response_model=List[HubResponse])
async def create_hubs(
    batch_id: int,
    hubs: List[HubCreate],
    db: Session = Depends(get_db)
):
    """Create multiple hubs for a batch"""
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    created_hubs = []
    for hub_data in hubs:
        # Map string values to enums
        hub_type_map = {
            "packhouse": HubType.PACKHOUSE,
            "x-dock": HubType.XDOCK,
            "cold-storage": HubType.COLDSTORAGE
        }
        
        energy_source_map = {
            "solar": EnergySource.SOLAR,
            "grid": EnergySource.GRID,
            "diesel": EnergySource.DIESEL,
            "wind": EnergySource.WIND
        }
        
        db_hub = Hub(
            batch_id=batch_id,
            type=hub_type_map.get(hub_data.type, HubType.PACKHOUSE),
            kwh=hub_data.kwh,
            energy_source=energy_source_map.get(hub_data.energy_source, EnergySource.GRID),
            hours=hub_data.hours,
            location=hub_data.location
        )
        db.add(db_hub)
        created_hubs.append(db_hub)
    
    db.commit()
    
    # Convert enum values to strings for response
    response_hubs = []
    for hub in created_hubs:
        response_hubs.append({
            "id": hub.id,
            "batch_id": hub.batch_id,
            "type": hub.type.value,
            "kwh": hub.kwh,
            "energy_source": hub.energy_source.value,
            "hours": hub.hours,
            "location": hub.location
        })
    
    return response_hubs

@router.get("/{batch_id}/hubs", response_model=List[HubResponse])
async def get_batch_hubs(batch_id: int, db: Session = Depends(get_db)):
    """Get all hubs for a batch"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    response_hubs = []
    for hub in batch.hubs:
        response_hubs.append({
            "id": hub.id,
            "batch_id": hub.batch_id,
            "type": hub.type.value,
            "kwh": hub.kwh,
            "energy_source": hub.energy_source.value,
            "hours": hub.hours,
            "location": hub.location
        })
    
    return response_hubs

@router.delete("/{batch_id}/hubs/{hub_id}")
async def delete_hub(batch_id: int, hub_id: int, db: Session = Depends(get_db)):
    """Delete a specific hub"""
    hub = db.query(Hub).filter(
        Hub.id == hub_id,
        Hub.batch_id == batch_id
    ).first()
    
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    
    db.delete(hub)
    db.commit()
    
    return {"message": "Hub deleted successfully"}