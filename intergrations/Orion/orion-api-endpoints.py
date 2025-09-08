# Sales Outreach Agent (Orion) - API Endpoints
# api/sales_routes.py

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Import our Orion agent
from agents.sales_outreach.orion_agent import SalesOutreachAgent, OutreachMode, LeadStatus

# Create router
router = APIRouter(prefix="/api/sales", tags=["sales"])

# Initialize Orion agent
orion_agent = SalesOutreachAgent()

# Pydantic models
class LeadDiscoveryCriteria(BaseModel):
    sector: str = Field(default="fresh produce importer", description="Industry sector to target")
    country: str = Field(default="Germany", description="Target country")
    keywords: List[str] = Field(default=["fresh produce", "importer"], description="Search keywords")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum leads to discover")

class EmailDraftRequest(BaseModel):
    lead_ids: Optional[List[str]] = Field(default=None, description="Specific lead IDs to draft for")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum emails to draft if no IDs specified")

class EmailBatch(BaseModel):
    emails: List[Dict[str, Any]] = Field(..., description="Batch of emails to send")

class LeadStatusUpdate(BaseModel):
    lead_id: str = Field(..., description="Lead ID to update")
    new_status: LeadStatus = Field(..., description="New status for the lead")
    notes: Optional[str] = Field(default=None, description="Additional notes")

class ModeChangeRequest(BaseModel):
    mode: OutreachMode = Field(..., description="New automation mode")

# Endpoints
@router.get("/status")
async def get_orion_status():
    """Get current status of Orion sales agent"""
    return {
        "agent": orion_agent.get_status(),
        "analytics": orion_agent.get_analytics(),
        "mode": orion_agent.mode.value,
        "daily_limit": orion_agent.daily_send_limit,
        "sent_today": orion_agent.sent_today
    }

@router.post("/discover-leads")
async def discover_leads(criteria: LeadDiscoveryCriteria, background_tasks: BackgroundTasks):
    """Discover new sales leads based on criteria"""
    try:
        # Run discovery in background for large requests
        if criteria.limit > 50:
            background_tasks.add_task(
                orion_agent.execute_task,
                {"type": "discover_leads", "criteria": criteria.dict()}
            )
            return {
                "status": "processing",
                "message": f"Discovering up to {criteria.limit} leads in background"
            }
        else:
            result = await orion_agent.execute_task({
                "type": "discover_leads",
                "criteria": criteria.dict()
            })
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/draft-emails")
async def draft_emails(request: EmailDraftRequest):
    """Draft personalized emails for leads"""
    try:
        result = await orion_agent.execute_task({
            "type": "draft_emails",
            "lead_ids": request.lead_ids
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-emails")
async def send_emails(batch: EmailBatch):
    """Send a batch of emails"""
    try:
        # Check mode restrictions
        if orion_agent.mode == OutreachMode.MANUAL:
            raise HTTPException(
                status_code=403,
                detail="Cannot send emails in MANUAL mode. Please change to SEMI_AUTO or FULLY_AUTO."
            )
        
        result = await orion_agent.execute_task({
            "type": "send_emails",
            "email_batch": batch.emails
        })
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-daily")
async def process_daily_outreach(background_tasks: BackgroundTasks):
    """Trigger daily outreach processing"""
    try:
        # Run in background
        background_tasks.add_task(
            orion_agent.execute_task,
            {"type": "process_daily_outreach"}
        )
        return {
            "status": "processing",
            "message": "Daily outreach processing started",
            "mode": orion_agent.mode.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-followups")
async def check_followups():
    """Check and send follow-up emails"""
    try:
        result = await orion_agent.execute_task({
            "type": "check_follow_ups"
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/lead-status")
async def update_lead_status(update: LeadStatusUpdate):
    """Update the status of a lead"""
    try:
        result = await orion_agent.execute_task({
            "type": "update_lead_status",
            "lead_id": update.lead_id,
            "new_status": update.new_status.value
        })
        
        # Add notes if provided
        if update.notes and "error" not in result:
            # This would update the lead's notes in the database
            pass
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leads")
async def get_leads(
    status: Optional[LeadStatus] = Query(None, description="Filter by status"),
    country: Optional[str] = Query(None, description="Filter by country"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    has_response: Optional[bool] = Query(None, description="Filter by response status"),
    limit: int = Query(50, ge=1, le=200, description="Maximum leads to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get leads with optional filtering"""
    try:
        # Load leads dataframe
        leads_df = orion_agent.leads_df.copy()
        
        # Apply filters
        if status:
            leads_df = leads_df[leads_df['status'] == status.value]
        if country:
            leads_df = leads_df[leads_df['country'].str.contains(country, case=False)]
        if sector:
            leads_df = leads_df[leads_df['sector'].str.contains(sector, case=False)]
        if has_response is not None:
            leads_df = leads_df[leads_df['response_received'] == has_response]
        
        # Sort by score and discovery date
        leads_df = leads_df.sort_values(['score', 'discovery_date'], ascending=[False, False])
        
        # Pagination
        total = len(leads_df)
        leads_df = leads_df.iloc[offset:offset + limit]
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "leads": leads_df.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_sales_analytics():
    """Get detailed sales analytics"""
    try:
        analytics = orion_agent.get_analytics()
        
        # Add time-based analytics
        if not orion_agent.leads_df.empty:
            leads_df = orion_agent.leads_df.copy()
            leads_df['discovery_date'] = pd.to_datetime(leads_df['discovery_date'])
            
            # Weekly discovery trend
            weekly_discoveries = leads_df.groupby(
                leads_df['discovery_date'].dt.to_period('W')
            ).size().to_dict()
            
            # Response time analysis
            responded_leads = leads_df[leads_df['response_received'] == True]
            if not responded_leads.empty:
                responded_leads['last_contact_date'] = pd.to_datetime(responded_leads['last_contact_date'])
                responded_leads['response_time_days'] = (
                    responded_leads['last_contact_date'] - responded_leads['discovery_date']
                ).dt.days
                avg_response_time = responded_leads['response_time_days'].mean()
            else:
                avg_response_time = None
            
            analytics.update({
                "weekly_discoveries": {str(k): v for k, v in weekly_discoveries.items()},
                "average_response_time_days": avg_response_time
            })
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/mode")
async def change_mode(request: ModeChangeRequest):
    """Change Orion's automation mode"""
    try:
        result = orion_agent.set_mode(request.mode)
        
        # Log mode change
        orion_agent.log_action(
            "mode_changed_via_api",
            {
                "old_mode": result["old_mode"],
                "new_mode": result["new_mode"],
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {
            "success": True,
            "result": result,
            "message": f"Mode changed to {request.mode.value}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve-emails")
async def approve_pending_emails(email_ids: List[str]):
    """Approve pending emails for sending"""
    try:
        # Get pending emails
        approved_emails = []
        
        for email_id in email_ids:
            # This would fetch the email from pending queue
            # For now, we'll simulate approval
            orion_agent.log_action(
                "email_approved",
                {
                    "email_id": email_id,
                    "approved_by": "api_user",
                    "timestamp": datetime.now().isoformat()
                }
            )
            approved_emails.append(email_id)
        
        return {
            "approved": len(approved_emails),
            "email_ids": approved_emails
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_email_templates():
    """Get available email templates"""
    return {
        "templates": list(orion_agent.email_templates.keys()),
        "count": len(orion_agent.email_templates)
    }

@router.get("/template/{template_name}")
async def get_email_template(template_name: str):
    """Get a specific email template"""
    if template_name not in orion_agent.email_templates:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    
    return {
        "name": template_name,
        "content": orion_agent.email_templates[template_name]
    }

# Health check
@router.get("/health")
async def health_check():
    """Check Orion agent health"""
    return {
        "status": "healthy",
        "agent_status": orion_agent.status.value,
        "mode": orion_agent.mode.value,
        "leads_loaded": len(orion_agent.leads_df) > 0,
        "templates_loaded": len(orion_agent.email_templates) > 0
    }

# Add to main FastAPI app
# In api/main.py, add:
# from api.sales_routes import router as sales_router
# app.include_router(sales_router)