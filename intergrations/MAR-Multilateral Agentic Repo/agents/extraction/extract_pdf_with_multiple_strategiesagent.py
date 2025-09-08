
class extract_pdf_with_multiple_strategiesAgent:
    """Agent based on extract_pdf_with_multiple_strategies from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_multi_model_extraction.py"""
    
    def __init__(self):
        self.name = "extract_pdf_with_multiple_strategiesAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Try multiple PDF extraction strategies"""
    strategies = []
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
        for encoding in ['utf-8', 'latin-1', 'ascii']:
            try:
                text_content = content.decode(encoding, errors='ignore')
                sentences = re.findall('[A-Z][A-Za-z\\s\\d,.\\-()%$]+[.!?]', text_content)
                number_units = re.findall('\\d+(?:,\\d{3})*(?:\\.\\d+)?\\s*(?:tCO2e|MWh|GWh|tonnes?|metric tons?|rate|incidents?|per\\s\\d+)', text_content, re.IGNORECASE)
                esg_patterns = []
                esg_terms = ['scope 1', 'scope 2', 'emissions', 'energy consumption', 'lost time', 'safety rate', 'LTCR', 'carbon', 'CO2']
                for term in esg_terms:
                    matches = re.findall(f'.{{0,150}}{re.escape(term)}.{{0,150}}', text_content, re.IGNORECASE)
                    esg_patterns.extend(matches)
                if sentences or number_units or esg_patterns:
                    combined_text = '\n'.join(sentences[:50]) + '\n\n' + '\n'.join(number_units[:20]) + '\n\n' + '\n'.join(esg_patterns[:30])
                    strategies.append({'method': f'binary_extraction_{encoding}', 'text': combined_text, 'sentences_found': len(sentences), 'numbers_found': len(number_units), 'esg_contexts': len(esg_patterns)})
            except Exception:
                continue
    except Exception as e:
        print(f'⚠️ Binary extraction failed: {e}')
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
        text_content = content.decode('latin-1', errors='ignore')
        table_patterns = re.findall('(\\d+(?:,\\d{3})*(?:\\.\\d+)?)\\s*([a-zA-Z\\s]{1,20})\\s*(\\d+(?:,\\d{3})*(?:\\.\\d+)?)', text_content)
        kpi_patterns = re.findall('([A-Z][a-z\\s]+(?:emissions?|energy|consumption|rate|incidents?))[:\\s]*(\\d+(?:,\\d{3})*(?:\\.\\d+)?)\\s*([a-zA-Z\\s]+)', text_content, re.IGNORECASE)
        if table_patterns or kpi_patterns:
            structured_text = 'STRUCTURED DATA FOUND:\n'
            for pattern in table_patterns[:10]:
                structured_text += f'Value: {pattern[0]} | Label: {pattern[1]} | Value2: {pattern[2]}\n'
            for pattern in kpi_patterns[:10]:
                structured_text += f'KPI: {pattern[0]} | Value: {pattern[1]} | Unit: {pattern[2]}\n'
            strategies.append({'method': 'structured_pattern_extraction', 'text': structured_text, 'table_patterns': len(table_patterns), 'kpi_patterns': len(kpi_patterns)})
    except Exception as e:
        print(f'⚠️ Structured extraction failed: {e}')
    if strategies:
        best_strategy = max(strategies, key=lambda x: len(x['text']))
        return {'success': True, 'text': best_strategy['text'], 'method': best_strategy['method'], 'all_strategies': strategies}
    else:
        return {'success': False, 'error': 'No extraction strategies succeeded', 'text': ''}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
