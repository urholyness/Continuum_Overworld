
class _ai_validate_search_resultsAgent:
    """Agent based on _ai_validate_search_results from ..\Rank_AI\01_search_discovery\ai_search_engine.py"""
    
    def __init__(self):
        self.name = "_ai_validate_search_resultsAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
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
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
