
class _extract_pdf_contentAgent:
    """Agent based on _extract_pdf_content from ..\Rank_AI\03_document_parsing\simple_esg_parser.py"""
    
    def __init__(self):
        self.name = "_extract_pdf_contentAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Multi-method PDF content extraction"""
    content = ''
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    content += page_text + '\n'
    except Exception:
    if not content:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + '\n'
        except Exception:
    return content.strip()
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
