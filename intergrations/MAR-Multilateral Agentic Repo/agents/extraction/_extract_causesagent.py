
class _extract_causesAgent:
    """Agent based on _extract_causes from ..\Nyxion\env\Lib\site-packages\pip\_vendor\resolvelib\resolvers\resolution.py"""
    
    def __init__(self):
        self.name = "_extract_causesAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract causes from list of criterion and deduplicate"""
    return list({id(i): i for c in criteron for i in c.information}.values())
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
