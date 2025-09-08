
class get_high_potential_discoveriesAgent:
    """Agent based on get_high_potential_discoveries from ..\MAR-Multilateral Agentic Repo\admin\omen_agent.py"""
    
    def __init__(self):
        self.name = "get_high_potential_discoveriesAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Get discoveries with high agent generation potential"""
    return [d for d in self.collected if d.agent_potential == 'high']
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
