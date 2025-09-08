
class extract_kpis_from_chunkAgent:
    """Agent based on extract_kpis_from_chunk from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_ai_extraction_chunked.py"""
    
    def __init__(self):
        self.name = "extract_kpis_from_chunkAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract KPIs from a single text chunk"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {'success': False, 'error': 'No API key', 'extractions': []}
    kpi_list = '\n'.join([f'- {kpi}' for kpi in target_kpis])
    prompt = f'\nYou are analyzing chunk {chunk_number} of {total_chunks} from an ESG report.\n\nTARGET KPIs TO FIND:\n{kpi_list}\n\nDOCUMENT CHUNK:\n{chunk_text}\n\nINSTRUCTIONS:\n1. Look for ANY of the target KPIs in this chunk\n2. Extract exact numerical values with units\n3. High confidence only if you find clear, unambiguous data\n4. If nothing clear is found in this chunk, return empty extractions\n\nRESPOND IN JSON:\n{{\n  "chunk_analysis": "{chunk_number}/{total_chunks}",\n  "extractions": [\n    {{\n      "kpi_name": "name",\n      "value": "number",\n      "unit": "unit",\n      "confidence": 85,\n      "source_text": "exact sentence",\n      "found": true\n    }}\n  ]\n}}\n'
    try:
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {'model': 'gpt-3.5-turbo', 'messages': [{'role': 'system', 'content': 'You are an ESG data extraction expert. Only extract data you are confident about.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.1, 'max_tokens': 1000}
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        if response.status_code != 200:
            return {'success': False, 'error': f'API error: {response.status_code}', 'extractions': []}
        ai_response = response.json()
        ai_content = ai_response['choices'][0]['message']['content']
        try:
            result = json.loads(ai_content)
            result['success'] = True
            return result
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Invalid JSON response', 'raw_response': ai_content, 'extractions': []}
    except Exception as e:
        return {'success': False, 'error': str(e), 'extractions': []}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
