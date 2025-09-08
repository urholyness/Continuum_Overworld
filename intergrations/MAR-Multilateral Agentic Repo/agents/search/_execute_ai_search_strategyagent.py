
class _execute_ai_search_strategyAgent:
    """Agent based on _execute_ai_search_strategy from ..\Rank_AI\01_search_discovery\ai_search_engine.py"""
    
    def __init__(self):
        self.name = "_execute_ai_search_strategyAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Execute a single AI-generated search strategy"""
    query = strategy.get('query', '')
    print(f'  🔍 Executing: {query}')
    try:
        search_url = 'https://www.googleapis.com/customsearch/v1'
        params = {'key': self.google_search_key, 'cx': self.google_cse_id, 'q': query, 'num': 10}
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_data = response.json()
        results = []
        for item in search_data.get('items', []):
            url = item.get('link', '')
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            ai_evaluation = self._ai_evaluate_search_result(url, title, snippet, company_name, year)
            if ai_evaluation['is_relevant']:
                result = SearchResult(url=url, title=title, ai_confidence=ai_evaluation['confidence'], ai_reasoning=ai_evaluation['reasoning'], source_type=ai_evaluation['source_type'], discovered_method=f'AI_SEARCH_STRATEGY: {query}', timestamp=datetime.now().isoformat())
                results.append(result)
        return results
    except Exception as e:
        print(f'  ❌ Search strategy failed: {e}')
        return []
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
