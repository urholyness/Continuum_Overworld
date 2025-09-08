
class AgentManagerAgent:
    """Agent based on AgentManager from ..\Orion\core\base_agent.py"""
    
    def __init__(self):
        self.name = "AgentManagerAgent"
        self.category = "automation"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
                self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger('AgentManager')
    def register_agent(self, agent: BaseAgent):
        """Register a new agent"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f'Agent registered: {agent.name} ({agent.agent_id})')
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        return [agent.get_status() for agent in self.agents.values()]
    def get_action_logs(self, agent_id: Optional[str]=None, limit: int=100) -> List[Dict[str, Any]]:
        """Get action logs for all agents or specific agent"""
        logs = []
        if agent_id:
            agent = self.get_agent(agent_id)
            if agent:
                logs = [log.to_dict() for log in agent.action_logs[-limit:]]
        else:
            for agent in self.agents.values():
                logs.extend([log.to_dict() for log in agent.action_logs[-limit:]])
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return logs[:limit]
    def approve_action(self, agent_id: str, action_index: int, approver: str) -> bool:
        """Approve a pending action"""
        agent = self.get_agent(agent_id)
        if agent and 0 <= action_index < len(agent.action_logs):
            log = agent.action_logs[action_index]
            if log.requires_approval:
                log.approved_by = approver
                log.status = 'approved'
                agent.status = AgentStatus.IDLE
                self.logger.info(f'Action approved: {log.action_type} by {approver}')
                return True
        return False
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
