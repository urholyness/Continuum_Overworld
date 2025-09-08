
class process_pdf_with_metadataAgent:
    """Agent based on process_pdf_with_metadata from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_enhanced.py"""
    
    def __init__(self):
        self.name = "process_pdf_with_metadataAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Process PDF with full metadata and greenwashing analysis with year tagging"""
    start_time = time.time()
    kpis = []
    greenwashing_analysis = None
    try:
        pdf_path = self.download_pdf(url)
        if not pdf_path:
            return (kpis, greenwashing_analysis)
        with pdfplumber.open(pdf_path) as pdf:
            report_name = pdf.metadata.get('Title', '') or url.split('/')[-1].replace('.pdf', '')
            if not report_name:
                report_name = f'{company} ESG Report'
            if not input_year:
                try:
                    creation_date = pdf.metadata.get('CreationDate', '')
                    if creation_date:
                        input_year = int(str(creation_date)[:4])
                except:
            logger.info(f'Processing {report_name} - {len(pdf.pages)} pages for year {input_year}')
            all_page_texts = []
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text() or ''
                    all_page_texts.append(page_text)
                    page_kpis = self.extract_kpis_from_page(page_text, page_num, company, ticker, url, report_name, input_year)
                    kpis.extend(page_kpis)
                    logger.info(f'Page {page_num}: {len(page_kpis)} KPIs extracted')
                except Exception as e:
                    logger.warning(f'Error processing page {page_num}: {e}')
                    continue
            full_text = ' '.join(all_page_texts)
            greenwashing_analysis = self.analyze_greenwashing(full_text, kpis, company, ticker, report_name, input_year)
        try:
            os.unlink(pdf_path)
        except:
        processing_time = time.time() - start_time
        logger.info(f'Processing complete: {len(kpis)} KPIs, greenwashing score: {greenwashing_analysis.overall_score:.1f}, time: {processing_time:.2f}s')
    except Exception as e:
        logger.error(f'Error processing PDF {url}: {e}')
    return (kpis, greenwashing_analysis)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
