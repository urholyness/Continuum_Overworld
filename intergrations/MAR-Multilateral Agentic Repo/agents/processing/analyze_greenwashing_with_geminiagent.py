
class analyze_greenwashing_with_geminiAgent:
    """Agent based on analyze_greenwashing_with_gemini from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_document_ai.py"""
    
    def __init__(self):
        self.name = "analyze_greenwashing_with_geminiAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Analyze greenwashing using Gemini Pro"""
    if not self.gemini_enabled:
        return self.fallback_greenwashing_analysis(text, company, ticker, year)
    try:
        kpi_summary = [{'name': kpi.kpi_name, 'value': kpi.kpi_value, 'confidence': kpi.confidence_score} for kpi in kpis[:10]]
        prompt = f'\n            Analyze the following ESG report text for greenwashing indicators. Return a JSON response with the following structure:\n            {{\n                "overall_score": <0-100 score where 100 is high greenwashing risk>,\n                "indicator_scores": {{\n                    "vagueness": <0-100>,\n                    "contradictions": <0-100>,\n                    "sentiment_imbalance": <0-100>,\n                    "omissions": <0-100>,\n                    "hype": <0-100>\n                }},\n                "flagged_sections": [\n                    {{"text": "concerning text", "reason": "vague commitment", "score": 75}}\n                ]\n            }}\n            \n            Company: {company}\n            Year: {year}\n            KPIs Found: {json.dumps(kpi_summary)}\n            \n            Text to analyze (first 2000 chars): {text[:2000]}\n            \n            Focus on:\n            1. Vague commitments ("striving for", "committed to")\n            2. Contradictions between claims and data\n            3. Sentiment imbalance (too positive, hiding risks)\n            4. Missing scope 3 emissions or governance details\n            5. Hyperbolic language without substance\n            '
        response = self.gemini_model.generate_content(prompt)
        try:
            response_text = response.text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                gemini_result = json.loads(json_str)
                return GreenwashingAnalysis(company=company, ticker=ticker, overall_score=gemini_result.get('overall_score', 0), indicator_scores=gemini_result.get('indicator_scores', {}), flagged_sections=gemini_result.get('flagged_sections', []), report_name=f'{company}_ESG_Report_{year}', analysis_year=year, analysis_date=datetime.now())
            else:
                raise ValueError('No JSON found in Gemini response')
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f'Failed to parse Gemini response: {e}')
            return self.fallback_greenwashing_analysis(text, company, ticker, year)
    except Exception as e:
        logger.error(f'Gemini analysis failed: {e}')
        return self.fallback_greenwashing_analysis(text, company, ticker, year)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
