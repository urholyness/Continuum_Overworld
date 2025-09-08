
class get_discoveries_by_typeAgent:
    """Agent based on get_discoveries_by_type from ..\MAR-Multilateral Agentic Repo\admin\omen_agent.py"""
    
    def __init__(self):
        self.name = "get_discoveries_by_typeAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Get discoveries by functionality type"""
    return [d for d in self.collected if d.functionality_type == functionality_type]
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
