
class extract_pdf_text_realAgent:
    """Agent based on extract_pdf_text_real from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_ai_extraction.py"""
    
    def __init__(self):
        self.name = "extract_pdf_text_realAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract text from actual PDF file using multiple methods"""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += f'\n--- Page {page_num + 1} ---\n{page_text}\n'
            if len(text.strip()) > 100:
                return {'success': True, 'text': text, 'pages': len(reader.pages), 'method': 'PyPDF2'}
    except ImportError:
        print('📦 PyPDF2 not available - trying alternative methods...')
    except Exception as e:
        print(f'⚠️ PyPDF2 extraction failed: {e}')
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ''
                text += f'\n--- Page {page_num + 1} ---\n{page_text}\n'
            if len(text.strip()) > 100:
                return {'success': True, 'text': text, 'pages': len(pdf.pages), 'method': 'pdfplumber'}
    except ImportError:
        print('📦 pdfplumber not available - trying pymupdf...')
    except Exception as e:
        print(f'⚠️ pdfplumber extraction failed: {e}')
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ''
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            text += f'\n--- Page {page_num + 1} ---\n{page_text}\n'
        doc.close()
        if len(text.strip()) > 100:
            return {'success': True, 'text': text, 'pages': len(doc), 'method': 'PyMuPDF'}
    except ImportError:
        print('📦 PyMuPDF not available - installing dependencies...')
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyMuPDF'])
            print('✅ PyMuPDF installed - retrying extraction...')
            import fitz
            doc = fitz.open(pdf_path)
            text = ''
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                text += f'\n--- Page {page_num + 1} ---\n{page_text}\n'
            doc.close()
            return {'success': True, 'text': text, 'pages': len(doc), 'method': 'PyMuPDF'}
        except Exception as install_error:
            print(f'❌ Failed to install PyMuPDF: {install_error}')
    except Exception as e:
        print(f'⚠️ PyMuPDF extraction failed: {e}')
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
        text_content = content.decode('latin-1', errors='ignore')
        import re
        readable_parts = re.findall('[A-Za-z\\s]{20,}', text_content)
        if readable_parts and len(''.join(readable_parts)) > 500:
            extracted_text = '\n'.join(readable_parts)
            return {'success': True, 'text': extracted_text, 'pages': 'unknown', 'method': 'binary_text_extraction', 'note': 'Extracted using binary text patterns - may be incomplete'}
    except Exception as e:
        print(f'⚠️ Binary text extraction failed: {e}')
    return {'success': False, 'error': 'All PDF extraction methods failed. Please install PyPDF2, pdfplumber, or PyMuPDF.', 'text': '', 'pages': 0}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
