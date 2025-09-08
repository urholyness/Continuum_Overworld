
class _ai_evaluate_search_resultAgent:
    """Agent based on _ai_evaluate_search_result from ..\Rank_AI\01_search_discovery\ai_search_engine.py"""
    
    def __init__(self):
        self.name = "_ai_evaluate_search_resultAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """AI evaluates if search result is relevant ESG report"""
    prompt = f'\nEvaluate if this search result is an official ESG/sustainability report.\n\nTARGET: {company_name} ESG report for {year}\n\nSEARCH RESULT:\nURL: {url}\nTitle: {title}\nSnippet: {snippet}\n\nAnalyze if this is:\n1. Official ESG/sustainability/corporate responsibility report\n2. For the correct company ({company_name})\n3. For the correct year ({year})\n4. From a credible source (company website, SEC filings, etc.)\n\nRESPOND IN JSON:\n{{\n  "is_relevant": true/false,\n  "confidence": 85,\n  "reasoning": "detailed explanation of assessment",\n  "source_type": "company_website|sec_filing|third_party|unknown",\n  "year_match": true/false,\n  "company_match": true/false\n}}\n'
    try:
        response = self._call_openai(prompt, max_tokens=800)
        return json.loads(response)
    except Exception as e:
        print(f'  ⚠️ AI evaluation failed: {e}')
        return self._fallback_evaluate_search_result(url, title, snippet, company_name, year)
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
