
class extract_with_openai_smartAgent:
    """Agent based on extract_with_openai_smart from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_multi_model_extraction.py"""
    
    def __init__(self):
        self.name = "extract_with_openai_smartAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Smart OpenAI extraction with chunking if needed"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {'success': False, 'error': 'No OpenAI API key', 'extractions': []}
    max_length = 12000 if model == 'gpt-4' else 8000
    if len(text) > max_length:
        chunks = []
        current_chunk = ''
        sections = text.split('\n\n')
        for section in sections:
            kpi_score = 0
            for kpi in target_kpis:
                kpi_words = kpi.lower().split()
                for word in kpi_words:
                    if word in section.lower():
                        kpi_score += 1
            section_priority = kpi_score > 0
            if len(current_chunk) + len(section) < max_length:
                current_chunk += section + '\n\n'
            else:
                if current_chunk:
                    chunks.append((current_chunk, section_priority))
                current_chunk = section + '\n\n'
        if current_chunk:
            chunks.append((current_chunk, False))
        chunks.sort(key=lambda x: x[1], reverse=True)
        text_to_analyze = chunks[0][0] if chunks else text[:max_length]
    else:
        text_to_analyze = text
    kpi_list = '\n'.join([f'- {kpi}' for kpi in target_kpis])
    prompt = f'\nYou are analyzing an ESG report. Find these specific KPIs with exact values and units:\n\nTARGET KPIs:\n{kpi_list}\n\nDOCUMENT TEXT:\n{text_to_analyze}\n\nIMPORTANT:\n- Extract ONLY if you find clear, unambiguous numerical values\n- Include exact units (tCO2e, MWh, rate per 200,000 hours, etc.)\n- Be conservative with confidence scores\n- Look for patterns like "Scope 1 emissions: 125,000 tCO2e" or "LTCR: 0.45 per 200,000 hours"\n\nJSON RESPONSE:\n{{\n  "extractions": [\n    {{\n      "kpi_name": "exact KPI name",\n      "value": "numerical value only",\n      "unit": "unit only", \n      "confidence": 85,\n      "source_text": "exact sentence where found",\n      "found": true\n    }}\n  ],\n  "analysis_summary": "what patterns were found in the document"\n}}\n'
    try:
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {'model': model, 'messages': [{'role': 'system', 'content': 'You are an expert ESG analyst. Only extract data you are completely confident about.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.0, 'max_tokens': 1500}
        print(f'🤖 Analyzing with {model}...')
        print(f'   Text length: {len(text_to_analyze):,} characters')
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        if response.status_code != 200:
            return {'success': False, 'error': f'{model} error: {response.text}', 'extractions': []}
        ai_response = response.json()
        ai_content = ai_response['choices'][0]['message']['content']
        try:
            result = json.loads(ai_content)
            result['success'] = True
            result['model_used'] = model
            result['text_analyzed_length'] = len(text_to_analyze)
            return result
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Invalid JSON from AI', 'raw_response': ai_content[:500], 'extractions': []}
    except Exception as e:
        return {'success': False, 'error': f'{model} failed: {str(e)}', 'extractions': []}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
