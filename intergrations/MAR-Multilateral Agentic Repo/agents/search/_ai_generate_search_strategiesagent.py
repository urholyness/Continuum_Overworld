
class _ai_generate_search_strategiesAgent:
    """Agent based on _ai_generate_search_strategies from ..\Rank_AI\01_search_discovery\ai_search_engine.py"""
    
    def __init__(self):
        self.name = "_ai_generate_search_strategiesAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """AI generates intelligent search strategies for ESG reports"""
    prompt = f'\nYou are an expert ESG analyst tasked with finding official ESG/sustainability reports.\n\nCOMPANY: {company_name}\nYEAR: {year}\n\nGenerate 5 intelligent search strategies to find the official ESG report. Consider:\n- Official company sustainability/ESG terminology\n- Common ESG report naming patterns\n- Corporate website structures\n- Regulatory filing locations\n- Alternative report names (sustainability, corporate responsibility, etc.)\n\nRESPOND IN JSON:\n{{\n  "strategies": [\n    {{\n      "query": "exact search query",\n      "reasoning": "why this search strategy will work",\n      "expected_sources": ["company website", "SEC filings", "investor relations"],\n      "confidence": 85\n    }}\n  ]\n}}\n'
    try:
        response = self._call_openai(prompt, max_tokens=1500)
        strategies_data = json.loads(response)
        return strategies_data.get('strategies', [])
    except Exception as e:
        print(f'⚠️ AI strategy generation failed: {e}')
        return [{'query': f'{company_name} {year} ESG report', 'reasoning': 'Primary ESG report search', 'expected_sources': ['company website'], 'confidence': 80}, {'query': f'{company_name} {year} sustainability report', 'reasoning': 'Alternative sustainability terminology', 'expected_sources': ['company website'], 'confidence': 75}, {'query': f'{company_name} {year} corporate responsibility report', 'reasoning': 'Corporate responsibility terminology', 'expected_sources': ['company website'], 'confidence': 70}, {'query': f'{company_name} {year} annual report ESG', 'reasoning': 'ESG section in annual reports', 'expected_sources': ['investor relations'], 'confidence': 65}, {'query': f'"{company_name}" "environmental sustainability report" {year}', 'reasoning': 'Exact phrase matching for environmental reports', 'expected_sources': ['company website', 'SEC filings'], 'confidence': 75}]
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
