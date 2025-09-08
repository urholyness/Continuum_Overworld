
class extract_with_gemini_smartAgent:
    """Agent based on extract_with_gemini_smart from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_multi_model_extraction.py"""
    
    def __init__(self):
        self.name = "extract_with_gemini_smartAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Smart Gemini extraction"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return {'success': False, 'error': 'No Gemini API key', 'extractions': []}
    if len(text) > 10000:
        kpi_relevant = []
        sentences = text.split('. ')
        for sentence in sentences:
            for kpi in target_kpis:
                if any((word.lower() in sentence.lower() for word in kpi.split())):
                    kqi_relevant.append(sentence)
                    break
        text_to_use = text[:5000] + '\n\nKPI RELEVANT SECTIONS:\n' + '\n'.join(kpi_relevant[:20])
        if len(text_to_use) > 10000:
            text_to_use = text_to_use[:10000]
    else:
        text_to_use = text
    kpi_list = '\n'.join([f'- {kpi}' for kpi in target_kpis])
    prompt = f'\nExtract these ESG KPIs from the document. Be precise and conservative.\n\nKPIs TO FIND:\n{kpi_list}\n\nDOCUMENT:\n{text_to_use}\n\nReturn JSON with exact numerical values and units:\n{{\n  "extractions": [\n    {{\n      "kpi_name": "name",\n      "value": "number",\n      "unit": "unit",\n      "confidence": 90,\n      "source_text": "source",\n      "found": true\n    }}\n  ]\n}}\n'
    try:
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}'
        data = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': 0.1, 'maxOutputTokens': 1000}}
        print(f'🤖 Analyzing with Gemini Pro...')
        print(f'   Text length: {len(text_to_use):,} characters')
        response = requests.post(url, json=data)
        if response.status_code != 200:
            return {'success': False, 'error': f'Gemini error: {response.text}', 'extractions': []}
        result = response.json()
        if 'candidates' in result and result['candidates']:
            ai_content = result['candidates'][0]['content']['parts'][0]['text']
            ai_content = ai_content.replace('```json', '').replace('```', '').strip()
            try:
                extraction_result = json.loads(ai_content)
                extraction_result['success'] = True
                extraction_result['model_used'] = 'gemini-pro'
                extraction_result['text_analyzed_length'] = len(text_to_use)
                return extraction_result
            except json.JSONDecodeError:
                return {'success': False, 'error': 'Invalid JSON from Gemini', 'raw_response': ai_content[:500], 'extractions': []}
        else:
            return {'success': False, 'error': 'No response from Gemini', 'extractions': []}
    except Exception as e:
        return {'success': False, 'error': f'Gemini failed: {str(e)}', 'extractions': []}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
