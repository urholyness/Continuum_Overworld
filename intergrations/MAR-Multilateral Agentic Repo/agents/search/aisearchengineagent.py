
class AISearchEngineAgent:
    """Agent based on AISearchEngine from ..\Rank_AI\01_search_discovery\ai_search_engine.py"""
    
    def __init__(self):
        self.name = "AISearchEngineAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Pure AI-powered ESG report discovery system"""
        """Initialize AI search engine with API keys"""
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.google_search_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        if not all([self.openai_key, self.google_search_key, self.google_cse_id]):
            raise ValueError('Missing required API keys for AI search engine')
    def discover_esg_reports(self, company_name: str, year: int) -> List[SearchResult]:
        """
        AI-driven discovery of ESG reports for company and year
        Uses pure AI reasoning - no regex patterns
        """
        print(f'🤖 AI Search Discovery: {company_name} ({year})')
        search_strategies = self._ai_generate_search_strategies(company_name, year)
        all_results = []
        for strategy in search_strategies:
            results = self._execute_ai_search_strategy(strategy, company_name, year)
            all_results.extend(results)
        validated_results = self._ai_validate_search_results(all_results, company_name, year)
        return validated_results
    def _ai_generate_search_strategies(self, company_name: str, year: int) -> List[Dict]:
        """AI generates intelligent search strategies for ESG reports"""
        prompt = f'\nYou are an expert ESG analyst tasked with finding official ESG/sustainability reports.\n\nCOMPANY: {company_name}\nYEAR: {year}\n\nGenerate 5 intelligent search strategies to find the official ESG report. Consider:\n- Official company sustainability/ESG terminology\n- Common ESG report naming patterns\n- Corporate website structures\n- Regulatory filing locations\n- Alternative report names (sustainability, corporate responsibility, etc.)\n\nRESPOND IN JSON:\n{{\n  "strategies": [\n    {{\n      "query": "exact search query",\n      "reasoning": "why this search strategy will work",\n      "expected_sources": ["company website", "SEC filings", "investor relations"],\n      "confidence": 85\n    }}\n  ]\n}}\n'
        try:
            response = self._call_openai(prompt, max_tokens=1500)
            strategies_data = json.loads(response)
            return strategies_data.get('strategies', [])
        except Exception as e:
            print(f'⚠️ AI strategy generation failed: {e}')
            return [{'query': f'{company_name} {year} ESG report', 'reasoning': 'Primary ESG report search', 'expected_sources': ['company website'], 'confidence': 80}, {'query': f'{company_name} {year} sustainability report', 'reasoning': 'Alternative sustainability terminology', 'expected_sources': ['company website'], 'confidence': 75}, {'query': f'{company_name} {year} corporate responsibility report', 'reasoning': 'Corporate responsibility terminology', 'expected_sources': ['company website'], 'confidence': 70}, {'query': f'{company_name} {year} annual report ESG', 'reasoning': 'ESG section in annual reports', 'expected_sources': ['investor relations'], 'confidence': 65}, {'query': f'"{company_name}" "environmental sustainability report" {year}', 'reasoning': 'Exact phrase matching for environmental reports', 'expected_sources': ['company website', 'SEC filings'], 'confidence': 75}]
    def _execute_ai_search_strategy(self, strategy: Dict, company_name: str, year: int) -> List[SearchResult]:
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
    def _ai_evaluate_search_result(self, url: str, title: str, snippet: str, company_name: str, year: int) -> Dict:
        """AI evaluates if search result is relevant ESG report"""
        prompt = f'\nEvaluate if this search result is an official ESG/sustainability report.\n\nTARGET: {company_name} ESG report for {year}\n\nSEARCH RESULT:\nURL: {url}\nTitle: {title}\nSnippet: {snippet}\n\nAnalyze if this is:\n1. Official ESG/sustainability/corporate responsibility report\n2. For the correct company ({company_name})\n3. For the correct year ({year})\n4. From a credible source (company website, SEC filings, etc.)\n\nRESPOND IN JSON:\n{{\n  "is_relevant": true/false,\n  "confidence": 85,\n  "reasoning": "detailed explanation of assessment",\n  "source_type": "company_website|sec_filing|third_party|unknown",\n  "year_match": true/false,\n  "company_match": true/false\n}}\n'
        try:
            response = self._call_openai(prompt, max_tokens=800)
            return json.loads(response)
        except Exception as e:
            print(f'  ⚠️ AI evaluation failed: {e}')
            return self._fallback_evaluate_search_result(url, title, snippet, company_name, year)
    def _ai_validate_search_results(self, results: List[SearchResult], company_name: str, year: int) -> List[SearchResult]:
        """AI validates and ranks all discovered results"""
        if not results:
            return []
        results_summary = []
        for i, result in enumerate(results):
            results_summary.append({'index': i, 'url': result.url, 'title': result.title, 'confidence': result.ai_confidence, 'reasoning': result.ai_reasoning})
        prompt = f"""\nReview these discovered ESG report candidates for {company_name} ({year}).\n\nCANDIDATES:\n{json.dumps(results_summary, indent=2)}\n\nPerform final AI validation:\n1. Remove duplicates or very similar URLs\n2. Rank by likelihood of being the official ESG report\n3. Flag any suspicious or irrelevant results\n4. Provide final confidence scores\n\nRESPOND IN JSON:\n{{\n  "validated_results": [\n    {{\n      "index": 0,\n      "final_confidence": 95,\n      "validation_reasoning": "why this is/isn't the official report",\n      "recommended_action": "download|investigate|reject"\n    }}\n  ],\n  "summary": "overall assessment of discovered reports"\n}}\n"""
        try:
            response = self._call_openai(prompt, max_tokens=2000)
            validation_data = json.loads(response)
            validated_results = []
            for validation in validation_data.get('validated_results', []):
                index = validation.get('index')
                if index < len(results) and validation.get('recommended_action') != 'reject':
                    result = results[index]
                    result.ai_confidence = validation.get('final_confidence', result.ai_confidence)
                    result.ai_reasoning += f" | AI Validation: {validation.get('validation_reasoning', '')}"
                    validated_results.append(result)
            validated_results.sort(key=lambda x: x.ai_confidence, reverse=True)
            return validated_results
        except Exception as e:
            print(f'⚠️ AI validation failed: {e}')
            results.sort(key=lambda x: x.ai_confidence, reverse=True)
            return results
    def _call_openai(self, prompt: str, max_tokens: int=1000) -> str:
        """Call OpenAI API with error handling"""
        headers = {'Authorization': f'Bearer {self.openai_key}', 'Content-Type': 'application/json'}
        data = {'model': 'gpt-4', 'messages': [{'role': 'system', 'content': 'You are an expert ESG analyst. Provide accurate, detailed analysis in the requested JSON format.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.1, 'max_tokens': max_tokens}
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    def _fallback_evaluate_search_result(self, url: str, title: str, snippet: str, company_name: str, year: int) -> Dict:
        """Rule-based evaluation when AI is unavailable (rate limited, etc.)"""
        url_lower = url.lower()
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        company_lower = company_name.lower()
        year_str = str(year)
        company_match = any([company_lower in url_lower, company_lower in title_lower, company_lower in snippet_lower])
        year_match = any([year_str in url_lower, year_str in title_lower, year_str in snippet_lower])
        esg_keywords = ['esg', 'sustainability', 'environmental', 'social', 'governance', 'corporate responsibility', 'responsible business', 'csr', 'sustainable development', 'climate', 'carbon', 'emissions']
        esg_match = any([keyword in title_lower or keyword in snippet_lower for keyword in esg_keywords])
        report_keywords = ['report', 'disclosure', 'statement', 'review']
        report_match = any([keyword in title_lower or keyword in snippet_lower for keyword in report_keywords])
        source_type = 'unknown'
        if any((domain in url_lower for domain in ['.com', '.org', '.net'])):
            if 'sec.gov' in url_lower:
                source_type = 'sec_filing'
            elif any((term in url_lower for term in ['investor', 'ir', 'annual'])):
                source_type = 'investor_relations'
            elif company_lower.replace(' ', '') in url_lower:
                source_type = 'company_website'
            else:
                source_type = 'third_party'
        confidence = 0
        if company_match:
            confidence += 30
        if year_match:
            confidence += 20
        if esg_match:
            confidence += 25
        if report_match:
            confidence += 15
        if source_type == 'company_website':
            confidence += 10
        elif source_type == 'sec_filing':
            confidence += 5
        is_relevant = company_match and (esg_match or report_match) and (confidence >= 50)
        reasoning_parts = []
        if company_match:
            reasoning_parts.append(f"Company '{company_name}' found in result")
        if year_match:
            reasoning_parts.append(f'Year {year} mentioned')
        if esg_match:
            reasoning_parts.append('ESG/sustainability keywords present')
        if report_match:
            reasoning_parts.append('Report-related keywords found')
        if source_type != 'unknown':
            reasoning_parts.append(f'Source identified as {source_type}')
        reasoning = 'Rule-based evaluation: ' + '; '.join(reasoning_parts) if reasoning_parts else 'No clear indicators found'
        return {'is_relevant': is_relevant, 'confidence': min(confidence, 95), 'reasoning': reasoning, 'source_type': source_type, 'year_match': year_match, 'company_match': company_match}
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
