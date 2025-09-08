
class extract_kpis_with_aiAgent:
    """Agent based on extract_kpis_with_ai from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_ai_extraction.py"""
    
    def __init__(self):
        self.name = "extract_kpis_with_aiAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """
    PURE AI EXTRACTION using OpenAI GPT - NO REGEX
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {'success': False, 'error': 'OpenAI API key not found. Set OPENAI_API_KEY environment variable.', 'extractions': []}
    kpi_list = '\n'.join([f'- {kpi}' for kpi in target_kpis])
    prompt = f'\nYou are an expert ESG data analyst. Extract the following specific KPIs from this document.\n\nTARGET KPIs TO EXTRACT:\n{kpi_list}\n\nDOCUMENT TEXT:\n{document_text}\n\nINSTRUCTIONS:\n1. Extract EXACT numerical values for each KPI\n2. Include proper units (e.g., tCO2e, MWh, rate per 200,000 hours)\n3. Provide confidence score (0-100) based on certainty\n4. Include the source sentence where you found each value\n5. If a KPI is not found, set confidence to 0 and value to null\n\nRESPOND IN STRICT JSON FORMAT:\n{{\n  "extractions": [\n    {{\n      "kpi_name": "Scope 1 Emissions (Global Operations)",\n      "value": "125000",\n      "unit": "metric tonnes",\n      "confidence": 95,\n      "source_sentence": "Our global operations generated 125,000 metric tonnes of Scope 1 emissions in 2023",\n      "extraction_method": "AI_ANALYSIS",\n      "found": true\n    }}\n  ],\n  "analysis_notes": "Brief summary of extraction quality",\n  "document_coverage": "Percentage of document analyzed"\n}}\n'
    try:
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {'model': 'gpt-4', 'messages': [{'role': 'system', 'content': 'You are an expert ESG analyst. Extract KPI data accurately and provide honest confidence scores.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.1, 'max_tokens': 2000}
        print('🤖 Sending document to OpenAI GPT-4 for analysis...')
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        if response.status_code != 200:
            return {'success': False, 'error': f'OpenAI API error: {response.status_code} - {response.text}', 'extractions': []}
        ai_response = response.json()
        ai_content = ai_response['choices'][0]['message']['content']
        try:
            extraction_result = json.loads(ai_content)
            extraction_result['success'] = True
            extraction_result['ai_model'] = 'gpt-4'
            extraction_result['extraction_timestamp'] = datetime.now().isoformat()
            return extraction_result
        except json.JSONDecodeError:
            return {'success': False, 'error': 'AI returned invalid JSON', 'raw_ai_response': ai_content, 'extractions': []}
    except Exception as e:
        return {'success': False, 'error': f'AI extraction failed: {str(e)}', 'extractions': []}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
