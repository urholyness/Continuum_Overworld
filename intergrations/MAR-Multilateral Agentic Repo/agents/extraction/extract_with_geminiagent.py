
class extract_with_geminiAgent:
    """Agent based on extract_with_gemini from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_document_ai_extraction.py"""
    
    def __init__(self):
        self.name = "extract_with_geminiAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract KPIs using Google Gemini"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return {'success': False, 'error': 'No Gemini API key', 'extractions': []}
    if len(text) > 10000:
        text = text[:10000] + '\\n[TEXT TRUNCATED]'
    kpi_list = '\\n'.join([f'- {kpi}' for kpi in target_kpis])
    prompt = f'\nExtract these specific KPIs from the ESG document:\n\n{kpi_list}\n\nDocument text:\n{text}\n\nFind exact numerical values with units. Return JSON format:\n{{\n  "extractions": [\n    {{\n      "kpi_name": "name",\n      "value": "number", \n      "unit": "unit",\n      "confidence": 90,\n      "source_text": "where found",\n      "found": true\n    }}\n  ]\n}}\n'
    try:
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}'
        data = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': 0.1, 'maxOutputTokens': 1000}}
        print(f'🤖 Sending to Google Gemini...')
        response = requests.post(url, json=data)
        if response.status_code != 200:
            return {'success': False, 'error': f'Gemini error: {response.text}', 'extractions': []}
        result = response.json()
        if 'candidates' in result and result['candidates']:
            ai_content = result['candidates'][0]['content']['parts'][0]['text']
            try:
                ai_content = ai_content.replace('```json', '').replace('```', '').strip()
                extraction_result = json.loads(ai_content)
                extraction_result['success'] = True
                extraction_result['model_used'] = 'gemini-pro'
                return extraction_result
            except json.JSONDecodeError:
                return {'success': False, 'error': 'Invalid JSON', 'raw_response': ai_content, 'extractions': []}
        else:
            return {'success': False, 'error': 'No response from Gemini', 'extractions': []}
    except Exception as e:
        return {'success': False, 'error': str(e), 'extractions': []}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
