
class _ai_extract_single_kpiAgent:
    """Agent based on _ai_extract_single_kpi from ..\Rank_AI\04_kpi_extraction\ai_kpi_extractor.py"""
    
    def __init__(self):
        self.name = "_ai_extract_single_kpiAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Use AI to extract a single KPI from content chunks with fallback"""
    for chunk_idx, chunk in enumerate(content_chunks):
        try:
            prompt = f'''\nYou are an expert ESG data analyst. Extract the specific KPI value from this ESG report content.\n\nTARGET KPI: {kpi_name}\nPOSSIBLE UNITS: {(', '.join(possible_units) if possible_units else 'Various units possible')}\n\nCONTENT TO ANALYZE:\n{chunk}\n\nYour task:\n1. Find mentions of "{kpi_name}" or closely related terms\n2. Extract the numerical value associated with this KPI\n3. Identify the unit of measurement\n4. Assess your confidence in the extraction\n\nRESPOND IN JSON FORMAT:\n{{\n  "found": true/false,\n  "value": numeric_value_only,\n  "unit": "detected_unit",\n  "confidence": 0.85,\n  "context": "sentence or phrase where you found the KPI",\n  "reasoning": "explanation of why this is the correct value"\n}}\n\nOnly respond with valid JSON. If the KPI is not found in this content, set "found": false.\n'''
            response = self._call_ai_api(prompt, openai_api_key)
            result = json.loads(response)
            if result.get('found') and result.get('value') is not None:
                llm_confidence = result.get('confidence', 0.85)
                claude_api_key = os.getenv('ANTHROPIC_API_KEY')
                if claude_api_key:
                    final_confidence = min(0.95, llm_confidence + 0.05)
                else:
                    final_confidence = min(0.9, llm_confidence)
                return KPIExtractionResult(kpi_key=kpi_key, kpi_name=kpi_name, value=float(result['value']), unit=result.get('unit'), confidence=final_confidence, source=f'llm_analysis_chunk_{chunk_idx}', extraction_method='pure_llm_analysis', patterns_matched=[], context_snippet=result.get('context', '')[:200])
        except Exception as e:
            if '429' in str(e) or 'Too Many Requests' in str(e):
                print(f'❌ LLM API rate limited for {kpi_key} - Cannot extract without AI')
            else:
                print(f'❌ LLM API failed for {kpi_key} in chunk {chunk_idx}: {e}')
            continue
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
