# Farm 5.0 Collaborative Agent System
# Core Infrastructure Setup

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import logging
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Agent Status Enum
class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"
    AWAITING_APPROVAL = "awaiting_approval"
    OFFLINE = "offline"

# Action Log Entry
@dataclass
class ActionLog:
    agent_id: str
    action_type: str
    action_data: Dict[str, Any]
    timestamp: datetime
    status: str
    requires_approval: bool = False
    approved_by: Optional[str] = None
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

# Base Agent Class
class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        self.action_logs: List[ActionLog] = []
        
    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary task"""
        pass
    
    def log_action(self, action_type: str, action_data: Dict[str, Any], 
                   status: str = "success", requires_approval: bool = False):
        """Log an action taken by the agent"""
        log_entry = ActionLog(
            agent_id=self.agent_id,
            action_type=action_type,
            action_data=action_data,
            timestamp=datetime.now(),
            status=status,
            requires_approval=requires_approval
        )
        self.action_logs.append(log_entry)
        self.logger.info(f"Action logged: {action_type} - Status: {status}")
        return log_entry
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "last_action": self.action_logs[-1].to_dict() if self.action_logs else None,
            "total_actions": len(self.action_logs)
        }

# Email Management Agent
class EmailManagementAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="email_manager_001",
            name="Email Management Agent",
            description="Handles email classification, auto-responses, and flagging"
        )
        self.email_categories = [
            "inquiry", "sales_opportunity", "support_request", 
            "internal_memo", "newsletter", "spam"
        ]
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email tasks"""
        self.status = AgentStatus.WORKING
        
        try:
            task_type = task_data.get("type")
            
            if task_type == "classify_email":
                result = await self.classify_email(task_data.get("email_data"))
            elif task_type == "generate_response":
                result = await self.generate_response(task_data.get("email_data"))
            elif task_type == "process_inbox":
                result = await self.process_inbox(task_data.get("emails", []))
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.status = AgentStatus.IDLE
            return result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.log_action("error", {"error": str(e)}, status="error")
            raise
    
    async def classify_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify an email into categories"""
        # Simulate AI classification (replace with actual OpenAI call)
        classification = {
            "email_id": email_data.get("id"),
            "category": "inquiry",  # This would be determined by AI
            "confidence": 0.85,
            "suggested_action": "auto_respond",
            "priority": "medium"
        }
        
        self.log_action("email_classified", classification)
        return classification
    
    async def generate_response(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an appropriate response to an email"""
        # Simulate AI response generation
        response = {
            "email_id": email_data.get("id"),
            "suggested_response": "Thank you for your inquiry about Farm 5.0...",
            "requires_approval": True,
            "confidence": 0.75
        }
        
        self.log_action("response_generated", response, requires_approval=True)
        self.status = AgentStatus.AWAITING_APPROVAL
        return response
    
    async def process_inbox(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple emails from inbox"""
        results = []
        for email in emails:
            classification = await self.classify_email(email)
            if classification["suggested_action"] == "auto_respond":
                response = await self.generate_response(email)
                results.append({
                    "email": email,
                    "classification": classification,
                    "response": response
                })
        
        summary = {
            "processed": len(emails),
            "auto_responses": len([r for r in results if r.get("response")]),
            "flagged_for_review": len([r for r in results if r.get("response", {}).get("requires_approval")])
        }
        
        self.log_action("inbox_processed", summary)
        return {"results": results, "summary": summary}

# Agent Manager
class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("AgentManager")
        
    def register_agent(self, agent: BaseAgent):
        """Register a new agent"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Agent registered: {agent.name} ({agent.agent_id})")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        return [agent.get_status() for agent in self.agents.values()]
    
    def get_action_logs(self, agent_id: Optional[str] = None, 
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Get action logs for all agents or specific agent"""
        logs = []
        
        if agent_id:
            agent = self.get_agent(agent_id)
            if agent:
                logs = [log.to_dict() for log in agent.action_logs[-limit:]]
        else:
            for agent in self.agents.values():
                logs.extend([log.to_dict() for log in agent.action_logs[-limit:]])
        
        # Sort by timestamp
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return logs[:limit]
    
    def approve_action(self, agent_id: str, action_index: int, approver: str) -> bool:
        """Approve a pending action"""
        agent = self.get_agent(agent_id)
        if agent and 0 <= action_index < len(agent.action_logs):
            log = agent.action_logs[action_index]
            if log.requires_approval:
                log.approved_by = approver
                log.status = "approved"
                agent.status = AgentStatus.IDLE
                self.logger.info(f"Action approved: {log.action_type} by {approver}")
                return True
        return False

# Dashboard Data Provider
class DashboardDataProvider:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all data needed for the dashboard"""
        return {
            "timestamp": datetime.now().isoformat(),
            "agents": self.agent_manager.get_all_agents_status(),
            "recent_actions": self.agent_manager.get_action_logs(limit=50),
            "pending_approvals": self._get_pending_approvals(),
            "system_metrics": self._get_system_metrics()
        }
    
    def _get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all actions awaiting approval"""
        pending = []
        for agent in self.agent_manager.agents.values():
            for i, log in enumerate(agent.action_logs):
                if log.requires_approval and not log.approved_by:
                    pending.append({
                        "agent_id": agent.agent_id,
                        "agent_name": agent.name,
                        "action_index": i,
                        "action": log.to_dict()
                    })
        return pending
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        total_actions = sum(len(agent.action_logs) for agent in self.agent_manager.agents.values())
        active_agents = sum(1 for agent in self.agent_manager.agents.values() 
                          if agent.status == AgentStatus.WORKING)
        
        return {
            "total_agents": len(self.agent_manager.agents),
            "active_agents": active_agents,
            "total_actions": total_actions,
            "pending_approvals": len(self._get_pending_approvals())
        }

# Example usage and initialization
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize the system
        manager = AgentManager()
        
        # Register Email Management Agent
        email_agent = EmailManagementAgent()
        manager.register_agent(email_agent)
        
        # Simulate email processing
        sample_emails = [
            {"id": "email_001", "subject": "Inquiry about Farm 5.0 pricing", "from": "customer@example.com"},
            {"id": "email_002", "subject": "Support request", "from": "user@example.com"},
            {"id": "email_003", "subject": "Partnership opportunity", "from": "partner@example.com"}
        ]
        
        # Process inbox
        result = await email_agent.execute_task({
            "type": "process_inbox",
            "emails": sample_emails
        })
        
        # Get dashboard data
        dashboard = DashboardDataProvider(manager)
        dashboard_data = dashboard.get_dashboard_data()
        
        print("Dashboard Data:")
        print(json.dumps(dashboard_data, indent=2))
        
        # Simulate approval
        pending = dashboard._get_pending_approvals()
        if pending:
            first_pending = pending[0]
            success = manager.approve_action(
                first_pending["agent_id"],
                first_pending["action_index"],
                "cto@greenstem.global"
            )
            print(f"\nApproval result: {success}")
    
    # Run the example
    asyncio.run(main())
