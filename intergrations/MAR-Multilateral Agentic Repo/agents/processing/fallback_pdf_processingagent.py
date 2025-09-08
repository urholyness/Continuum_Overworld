
class fallback_pdf_processingAgent:
    """Agent based on fallback_pdf_processing from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_document_ai.py"""
    
    def __init__(self):
        self.name = "fallback_pdf_processingAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Fallback PDF processing using pdfplumber"""
    logger.info(f'🔄 Using fallback PDF processing for {company} due to Document AI failure')
    logger.debug(f'📄 Fallback processing PDF: {len(pdf_content)} bytes for {company} ({year})')
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(pdf_content)
        tmp_path = tmp_file.name
    try:
        kpis = []
        text_pages = []
        with pdfplumber.open(tmp_path) as pdf:
            total_pages = len(pdf.pages)
            start_page = max(0, int(total_pages * 0.1))
            end_page = int(total_pages * 0.95)
            for page_idx in range(start_page, min(end_page, total_pages)):
                page = pdf.pages[page_idx]
                page_text = page.extract_text() or ''
                text_pages.append(page_text)
                page_kpis = self.fallback_extraction([page_text], company, ticker, year, page_idx)
                kpis.extend(page_kpis)
        full_text = ' '.join(text_pages)
        greenwashing = self.analyze_greenwashing_with_gemini(full_text, kpis, company, ticker, year)
        return (kpis, greenwashing)
    finally:
        os.unlink(tmp_path)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
