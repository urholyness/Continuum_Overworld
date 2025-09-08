
class extract_pdf_text_improvedAgent:
    """Agent based on extract_pdf_text_improved from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_ai_extraction_chunked.py"""
    
    def __init__(self):
        self.name = "extract_pdf_text_improvedAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract text from PDF with better cleaning"""
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
        text_content = content.decode('latin-1', errors='ignore')
        sentences = re.findall('[A-Z][a-z\\s\\d,.\\-()%]{10,}[.!?]', text_content)
        number_patterns = re.findall('\\d+[,.\\d]*\\s*[A-Za-z]+', text_content)
        esg_contexts = []
        esg_terms = ['scope', 'emission', 'energy', 'lost time', 'safety', 'carbon', 'CO2', 'tCO2e', 'MWh', 'rate']
        for term in esg_terms:
            pattern = f'.{{0,100}}{term}.{{0,100}}'
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            esg_contexts.extend(matches)
        all_text = []
        all_text.extend(sentences)
        all_text.extend([f'Number pattern: {np}' for np in number_patterns[:20]])
        all_text.extend(esg_contexts)
        extracted_text = '\n'.join(all_text)
        if len(extracted_text) > 500:
            return {'success': True, 'text': extracted_text, 'pages': 'unknown', 'method': 'improved_binary_extraction', 'note': 'Extracted key sentences and ESG-relevant text patterns'}
    except Exception as e:
        print(f'⚠️ Improved extraction failed: {e}')
    return {'success': False, 'error': 'Could not extract meaningful text from PDF', 'text': '', 'pages': 0}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
