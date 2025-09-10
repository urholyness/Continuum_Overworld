from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional
import json
import os

from models import get_db, Batch, Result
from calc.iso14083 import ISO14083Calculator
from calc.glec import GLECCalculator
from calc.ghg_protocol import GHGProtocolMapper

router = APIRouter()

class CalculationRequest(BaseModel):
    factor_pack: str = "DEFRA-2024"
    rf: bool = True

class CalculationResponse(BaseModel):
    iso14083: Dict
    glec: Dict
    ghg_protocol: Dict
    intensity: float
    cbam_ready: bool

@router.post("/{batch_id}/calculate", response_model=CalculationResponse)
async def calculate_emissions(
    batch_id: int,
    request: CalculationRequest = CalculationRequest(),
    db: Session = Depends(get_db)
):
    """
    Calculate emissions for a batch using ISO 14083, GLEC, and GHG Protocol methodologies
    """
    # Get batch with all relationships
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    if not batch.legs:
        raise HTTPException(status_code=400, detail="Batch has no transport legs")
    
    # Initialize calculators
    iso_calc = ISO14083Calculator(db, request.factor_pack)
    glec_calc = GLECCalculator()
    ghg_mapper = GHGProtocolMapper()
    
    # Perform calculations
    iso_results = iso_calc.calculate_batch(batch, rf_apply=request.rf)
    glec_results = glec_calc.calculate_glec_summary(batch, iso_results)
    ghg_results = ghg_mapper.map_to_scopes(batch, iso_results, glec_results)
    
    # Store results in database
    db_result = Result(
        batch_id=batch_id,
        iso14083_json=iso_results,
        glec_json=glec_results,
        ghg_scopes_json=ghg_results,
        intensity_kgco2e_per_kg=iso_results["totals"]["intensity_kgco2e_per_kg"]
    )
    
    # Generate CBAM snippet
    cbam_snippet = _generate_cbam_snippet(batch, iso_results, ghg_results, request)
    db_result.cbam_snippet = cbam_snippet
    
    db.add(db_result)
    db.commit()
    
    return {
        "iso14083": iso_results,
        "glec": glec_results,
        "ghg_protocol": ghg_results,
        "intensity": iso_results["totals"]["intensity_kgco2e_per_kg"],
        "cbam_ready": batch.project.cbam_flag if batch.project else False
    }

@router.get("/{batch_id}/cbam-snippet")
async def get_cbam_snippet(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    Get CBAM-ready embedded emissions snippet for a batch
    """
    # Get latest calculation result
    result = db.query(Result).filter(
        Result.batch_id == batch_id
    ).order_by(Result.created_at.desc()).first()
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No calculation results found. Please calculate emissions first."
        )
    
    if not result.cbam_snippet:
        # Generate snippet if not stored
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        result.cbam_snippet = _generate_cbam_snippet(
            batch,
            result.iso14083_json,
            result.ghg_scopes_json,
            CalculationRequest()
        )
        db.commit()
    
    return Response(
        content=result.cbam_snippet,
        media_type="text/plain"
    )

@router.get("/{batch_id}/results/latest")
async def get_latest_results(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the latest calculation results for a batch
    """
    result = db.query(Result).filter(
        Result.batch_id == batch_id
    ).order_by(Result.created_at.desc()).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="No calculation results found")
    
    return {
        "batch_id": batch_id,
        "iso14083": result.iso14083_json,
        "glec": result.glec_json,
        "ghg_protocol": result.ghg_scopes_json,
        "intensity": result.intensity_kgco2e_per_kg,
        "calculated_at": result.created_at
    }

def _generate_cbam_snippet(
    batch: Batch,
    iso_results: Dict,
    ghg_results: Dict,
    request: CalculationRequest
) -> str:
    """
    Generate CBAM-compliant embedded emissions snippet
    """
    total_emissions = ghg_results["total_tco2e"]
    
    # Check if RF was applied to any air legs
    rf_status = "off"
    for leg_result in iso_results.get("legs", []):
        if leg_result.get("rf_applied"):
            rf_status = "on"
            break
    
    # Generate upstream/downstream split
    cat4_emissions = ghg_results["scope3"]["categories"]["4"]["emissions_tco2e"]
    cat9_emissions = ghg_results["scope3"]["categories"]["9"]["emissions_tco2e"]
    
    snippet = f"""Embedded emissions for batch {batch.project_tag or batch.id}: {total_emissions:.3f} tCO₂e (ISO 14083-conform; GLEC-mapped TTW/WTT).

Calculation methodology:
- Standard: ISO 14083:2023 with GLEC Framework v3.0
- Factors: {request.factor_pack}
- Air Radiative Forcing: {rf_status}

Scope allocation (GHG Protocol):
- Scope 1 (Direct): {ghg_results['scope1']['emissions_tco2e']:.3f} tCO₂e
- Scope 2 (Electricity): {ghg_results['scope2']['emissions_tco2e']:.3f} tCO₂e
- Scope 3, Category 4 (Upstream T&D): {cat4_emissions:.3f} tCO₂e
- Scope 3, Category 9 (Downstream T&D): {cat9_emissions:.3f} tCO₂e

Product carbon intensity: {iso_results['totals']['intensity_kgco2e_per_kg']:.3f} kgCO₂e/kg

This calculation includes:
- {len(iso_results.get('legs', []))} transport legs with TTW/WTT split
- {len(iso_results.get('hubs', []))} hub activities (packhouse, cold storage)
- Mass-distance allocation per GLEC Framework
- Load factor and backhaul adjustments where applicable

Verification: Factor provenance tracked per leg. Primary carrier data integration available.

Generated: {batch.created_at.isoformat()}
CBAM-ready: Embedded emissions calculated per EU CBAM requirements."""
    
    return snippet