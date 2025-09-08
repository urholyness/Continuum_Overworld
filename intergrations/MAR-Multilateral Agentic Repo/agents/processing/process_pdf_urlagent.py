
class process_pdf_urlAgent:
    """Agent based on process_pdf_url from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor.py"""
    
    def __init__(self):
        self.name = "process_pdf_urlAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """
        Process a single PDF URL to extract KPIs
        Args:
            company (str): Company name
            ticker (str): Stock ticker
            url (str): PDF URL
        Returns:
            ExtractionResult: Processing results
        """
    start_time = time.time()
    cache_key = f'kpi_extraction:{company}:{url}'
    if self.redis_client:
        try:
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                logger.info(f'Cache hit for KPI extraction: {company}')
                cached_data = json.loads(cached_result)
                return ExtractionResult(**cached_data)
        except Exception as e:
            logger.warning(f'Cache read failed: {e}')
    logger.info(f'Processing PDF for {company}: {url}')
    try:
        pdf_content = self.download_pdf(url)
        if not pdf_content:
            return ExtractionResult(company=company, ticker=ticker, source_url=url, kpis_extracted=[], processing_time=time.time() - start_time, success=False, error_message='Failed to download PDF')
        text = self.extract_text_document_ai(pdf_content)
        if not text:
            logger.info(f'Falling back to local PDF extraction for {company}')
            text = self.extract_text_fallback(pdf_content)
        if not text:
            return ExtractionResult(company=company, ticker=ticker, source_url=url, kpis_extracted=[], processing_time=time.time() - start_time, success=False, error_message='Failed to extract text from PDF')
        kpis_regex = self.extract_kpis_regex(text)
        kpis_openai = self.extract_kpis_openai(text)
        all_kpis = kpis_regex + kpis_openai
        for kpi in all_kpis:
            kpi.company = company
            kpi.ticker = ticker
            kpi.source_url = url
        unique_kpis = self._deduplicate_kpis(all_kpis)
        result = ExtractionResult(company=company, ticker=ticker, source_url=url, kpis_extracted=unique_kpis, processing_time=time.time() - start_time, success=True, text_length=len(text), document_pages=len(pdf_content) // 1000)
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, 3600, json.dumps(asdict(result)))
                logger.info(f'Cached result for {company}')
            except Exception as e:
                logger.warning(f'Cache write failed: {e}')
        self._save_extraction_result(result)
        logger.info(f'Successfully extracted {len(unique_kpis)} KPIs for {company}')
        return result
    except Exception as e:
        error_msg = f'Error processing PDF: {e}'
        logger.error(f'Processing failed for {company}: {error_msg}')
        return ExtractionResult(company=company, ticker=ticker, source_url=url, kpis_extracted=[], processing_time=time.time() - start_time, success=False, error_message=error_msg)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
