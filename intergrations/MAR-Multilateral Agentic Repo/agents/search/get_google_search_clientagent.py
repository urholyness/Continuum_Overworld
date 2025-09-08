
class get_google_search_clientAgent:
    """Agent based on get_google_search_client from ..\Nyxion\backend\integrations\google_search.py"""
    
    def __init__(self):
        self.name = "get_google_search_clientAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Get or create Google Search client instance"""
    global _google_search_client
    if _google_search_client is None:
        _google_search_client = GoogleSearchClient()
    return _google_search_client
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
