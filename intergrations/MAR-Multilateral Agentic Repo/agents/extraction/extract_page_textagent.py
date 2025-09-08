
class extract_page_textAgent:
    """Agent based on extract_page_text from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_document_ai.py"""
    
    def __init__(self):
        self.name = "extract_page_textAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract text from Document AI page"""
    text_segments = []
    for text_anchor in page.layout.text_anchor.text_segments:
        start_index = text_anchor.start_index
        end_index = text_anchor.end_index
        text_segments.append(page.text[start_index:end_index])
    return ' '.join(text_segments)
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
