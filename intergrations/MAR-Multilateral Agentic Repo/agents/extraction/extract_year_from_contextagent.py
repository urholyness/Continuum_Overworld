
class extract_year_from_contextAgent:
    """Agent based on extract_year_from_context from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_document_ai.py"""
    
    def __init__(self):
        self.name = "extract_year_from_contextAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract year from PDF content"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(pdf_content)
            tmp_path = tmp_file.name
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages[:3]:
                text = page.extract_text() or ''
                year_matches = re.findall('\\b(20[12][0-9])\\b', text)
                if year_matches:
                    return int(max(year_matches))
        os.unlink(tmp_path)
    except Exception:
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
