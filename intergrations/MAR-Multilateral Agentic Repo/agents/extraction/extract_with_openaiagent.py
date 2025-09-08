
class extract_with_openaiAgent:
    """Agent based on extract_with_openai from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_document_ai_extraction.py"""
    
    def __init__(self):
        self.name = "extract_with_openaiAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract KPIs using OpenAI models"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {'success': False, 'error': 'No OpenAI API key', 'extractions': []}
    max_text_length = 12000 if model == 'gpt-4' else 8000
    if len(text) > max_text_length:
        text = text[:max_text_length] + '\\n[TEXT TRUNCATED]'
    kpi_list = '\\n'.join([f'- {kpi}' for kpi in target_kpis])
    prompt = f"""\nExtract the following KPIs from this ESG document:\n\nTARGET KPIs:\n{kpi_list}\n\nDOCUMENT TEXT:\n{text}\n\nExtract exact numerical values and units. Be precise and conservative - only extract if you're confident.\n\nRESPOND IN JSON:\n{{\n  "extractions": [\n    {{\n      "kpi_name": "exact name",\n      "value": "numerical value",\n      "unit": "unit",\n      "confidence": 85,\n      "source_text": "source sentence",\n      "found": true\n    }}\n  ],\n  "model_analysis": "brief summary of what was found"\n}}\n"""
    try:
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {'model': model, 'messages': [{'role': 'system', 'content': 'You are an expert ESG analyst. Extract KPI data accurately.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.1, 'max_tokens': 1500}
        print(f'🤖 Sending to OpenAI {model}...')
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        if response.status_code != 200:
            return {'success': False, 'error': f'OpenAI error: {response.text}', 'extractions': []}
        ai_response = response.json()
        ai_content = ai_response['choices'][0]['message']['content']
        try:
            result = json.loads(ai_content)
            result['success'] = True
            result['model_used'] = model
            return result
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Invalid JSON', 'raw_response': ai_content, 'extractions': []}
    except Exception as e:
        return {'success': False, 'error': str(e), 'extractions': []}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
