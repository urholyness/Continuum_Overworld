
class extract_pdf_textAgent:
    """Agent based on extract_pdf_text from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_pdf_simple.py"""
    
    def __init__(self):
        self.name = "extract_pdf_textAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract text from PDF using available methods"""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += f'\n--- Page {page_num + 1} ---\n{page_text}\n'
            return {'success': True, 'text': text, 'pages': len(reader.pages), 'method': 'PyPDF2'}
    except ImportError:
    except Exception as e:
        print(f'PyPDF2 extraction failed: {e}')
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ''
                text += f'\n--- Page {page_num + 1} ---\n{page_text}\n'
            return {'success': True, 'text': text, 'pages': len(pdf.pages), 'method': 'pdfplumber'}
    except ImportError:
    except Exception as e:
        print(f'pdfplumber extraction failed: {e}')
    return {'success': False, 'error': 'No PDF libraries available', 'text': '', 'pages': 0}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
