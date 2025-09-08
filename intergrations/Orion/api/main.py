# Farm 5.0 Agent System - FastAPI Service
# api_service.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

# Import our core system (from previous file)
# from farm5_agent_core import AgentManager, EmailManagementAgent, DashboardDataProvider

app = FastAPI(title="Farm 5.0 Agent System API", version="1.0.0")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent system
agent_manager = AgentManager()
email_agent = EmailManagementAgent()
agent_manager.register_agent(email_agent)
dashboard_provider = DashboardDataProvider(agent_manager)

# Pydantic models for API
class TaskRequest(BaseModel):
    agent_id: str
    task_type: str
    task_data: Dict[str, Any]

class ApprovalRequest(BaseModel):
    agent_id: str
    action_index: int
    approver: str

class EmailProcessRequest(BaseModel):
    emails: List[Dict[str, Any]]

# API Endpoints
@app.get("/")
async def root():
    return {
        "service": "Farm 5.0 Agent System",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/dashboard")
async def get_dashboard():
    """Get complete dashboard data"""
    return dashboard_provider.get_dashboard_data()

@app.get("/api/agents")
async def get_agents():
    """Get all registered agents and their status"""
    return agent_manager.get_all_agents_status()

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.get_status()

@app.get("/api/logs")
async def get_logs(agent_id: Optional[str] = None, limit: int = 100):
    """Get action logs"""
    return {
        "logs": agent_manager.get_action_logs(agent_id, limit),
        "count": len(agent_manager.get_action_logs(agent_id, limit))
    }

@app.post("/api/tasks/execute")
async def execute_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Execute a task on a specific agent"""
    agent = agent_manager.get_agent(request.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        # Execute task asynchronously
        result = await agent.execute_task({
            "type": request.task_type,
            **request.task_data
        })
        return {
            "status": "success",
            "result": result,
            "agent_status": agent.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/email/process")
async def process_emails(request: EmailProcessRequest):
    """Process a batch of emails"""
    try:
        result = await email_agent.execute_task({
            "type": "process_inbox",
            "emails": request.emails
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/actions/approve")
async def approve_action(request: ApprovalRequest):
    """Approve a pending action"""
    success = agent_manager.approve_action(
        request.agent_id,
        request.action_index,
        request.approver
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Could not approve action")
    
    return {
        "status": "approved",
        "agent_id": request.agent_id,
        "action_index": request.action_index,
        "approver": request.approver
    }

@app.get("/api/pending-approvals")
async def get_pending_approvals():
    """Get all pending approvals"""
    return dashboard_provider._get_pending_approvals()

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    return dashboard_provider._get_system_metrics()

# WebSocket endpoint for real-time updates (optional)
from fastapi import WebSocket
import json

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send dashboard updates every 5 seconds
            dashboard_data = dashboard_provider.get_dashboard_data()
            await websocket.send_text(json.dumps(dashboard_data))
            await asyncio.sleep(5)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agents": len(agent_manager.agents),
        "timestamp": datetime.now().isoformat()
    }

# To run the server:
# uvicorn api_service:app --reload --host 0.0.0.0 --port 8000
