from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

from models import get_db, Batch, Project

router = APIRouter()

class BatchCreate(BaseModel):
    project_tag: str = Field(..., example="GSG-FB-2025-W34")
    commodity: str = Field(..., example="French beans")
    net_mass_kg: float = Field(..., example=1000)
    packaging_mass_kg: float = Field(80, example=80)
    harvest_week: str = Field(None, example="2025-W34")
    ownership: str = Field("3PL", example="3PL")

class BatchResponse(BaseModel):
    id: int
    project_tag: str
    commodity: str
    net_mass_kg: float
    packaging_mass_kg: float
    harvest_week: str
    ownership: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=BatchResponse)
async def create_batch(batch: BatchCreate, db: Session = Depends(get_db)):
    """Create a new batch"""
    db_batch = Batch(
        project_tag=batch.project_tag,
        commodity=batch.commodity,
        net_mass_kg=batch.net_mass_kg,
        pkg_mass_kg=batch.packaging_mass_kg,
        harvest_week=batch.harvest_week,
        ownership=batch.ownership
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(batch_id: int, db: Session = Depends(get_db)):
    """Get batch by ID"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

@router.get("/", response_model=List[BatchResponse])
async def list_batches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all batches"""
    batches = db.query(Batch).offset(skip).limit(limit).all()
    return batches

@router.post("/{batch_id}/duplicate", response_model=BatchResponse)
async def duplicate_batch(batch_id: int, db: Session = Depends(get_db)):
    """Duplicate an existing batch with its legs and hubs"""
    original = db.query(Batch).filter(Batch.id == batch_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Create new batch
    new_batch = Batch(
        project_tag=f"{original.project_tag}-copy",
        commodity=original.commodity,
        net_mass_kg=original.net_mass_kg,
        pkg_mass_kg=original.pkg_mass_kg,
        harvest_week=original.harvest_week,
        ownership=original.ownership
    )
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    
    # Copy legs
    for leg in original.legs:
        new_leg = type(leg)(**{
            c.key: getattr(leg, c.key)
            for c in leg.__table__.columns
            if c.key not in ['id', 'batch_id']
        })
        new_leg.batch_id = new_batch.id
        db.add(new_leg)
    
    # Copy hubs
    for hub in original.hubs:
        new_hub = type(hub)(**{
            c.key: getattr(hub, c.key)
            for c in hub.__table__.columns
            if c.key not in ['id', 'batch_id']
        })
        new_hub.batch_id = new_batch.id
        db.add(new_hub)
    
    db.commit()
    db.refresh(new_batch)
    return new_batch