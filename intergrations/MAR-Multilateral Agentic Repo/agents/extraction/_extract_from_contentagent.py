
class _extract_from_contentAgent:
    """Agent based on _extract_from_content from ..\Rank_AI\04_kpi_extraction\ai_kpi_extractor.py"""
    
    def __init__(self):
        self.name = "_extract_from_contentAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract KPIs from raw content using pure AI analysis"""
    results = {}
    if not content:
        return results
    openai_api_key = os.getenv('OPENAI_API_KEY')
    claude_api_key = os.getenv('ANTHROPIC_API_KEY')
    if not openai_api_key and (not claude_api_key):
        print('❌ No LLM API keys available - Pure AI extraction requires OpenAI or Claude API')
        print('   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable')
        return results
    print(f"✅ Using pure LLM extraction (Claude: {('✓' if claude_api_key else '✗')}, OpenAI: {('✓' if openai_api_key else '✗')})")
    content_chunks = self._split_content_for_ai(content, max_chunk_size=3000)
    for kpi_key, kpi_config in target_kpis.items():
        kpi_name = kpi_config['name']
        possible_units = kpi_config.get('units', [])
        extraction_result = self._ai_extract_single_kpi(content_chunks, kpi_key, kpi_name, possible_units, openai_api_key)
        if extraction_result:
            results[kpi_key] = extraction_result
            print(f'✅ {kpi_key}: {extraction_result.value} {extraction_result.unit} (LLM confidence: {extraction_result.confidence:.0%})')
        else:
            print(f'❌ {kpi_key}: Not found by LLM analysis')
    return results
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
