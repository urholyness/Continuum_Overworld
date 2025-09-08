
class save_discoveriesAgent:
    """Agent based on save_discoveries from ..\MAR-Multilateral Agentic Repo\admin\omen_agent.py"""
    
    def __init__(self):
        self.name = "save_discoveriesAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Save detailed discoveries for agent generation"""
    self.discoveries_path.parent.mkdir(parents=True, exist_ok=True)
    discoveries_data = [asdict(discovery) for discovery in self.collected]
    with open(self.discoveries_path, 'w') as f:
        json.dump(discoveries_data, f, indent=2)
    print(f'💾 Saved {len(discoveries_data)} code discoveries to {self.discoveries_path}')
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
