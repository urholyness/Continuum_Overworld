
class process_pdf_with_document_aiAgent:
    """Agent based on process_pdf_with_document_ai from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_document_ai.py"""
    
    def __init__(self):
        self.name = "process_pdf_with_document_aiAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Process PDF using Document AI for enhanced accuracy with comprehensive error handling"""
    logger.info(f'🔄 Starting Document AI processing for {company} ({year})')
    logger.debug(f'📊 PDF content size: {len(pdf_content)} bytes, Processor: {self.processor_name}')
    if not self.document_ai_enabled:
        logger.warning(f'⚠️  Document AI not enabled for {company}, using fallback')
        return self.fallback_pdf_processing(pdf_content, company, ticker, year)
    if len(pdf_content) < 1024:
        logger.warning(f'⚠️  PDF content suspiciously small ({len(pdf_content)} bytes) for {company}')
    if not pdf_content.startswith(b'%PDF'):
        logger.error(f"❌ Invalid PDF header for {company} - content does not start with '%PDF'")
        return self.fallback_pdf_processing(pdf_content, company, ticker, year)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f'🚀 Creating Document AI request for {company} (attempt {attempt + 1}/{max_retries})')
            raw_document = documentai.RawDocument(content=pdf_content, mime_type='application/pdf')
            request = documentai.ProcessRequest(name=self.processor_name, raw_document=raw_document)
            logger.debug(f'📤 Sending request to Document AI for {company}...')
            start_time = time.time()
            result = self.doc_ai_client.process_document(request=request)
            processing_time = time.time() - start_time
            document = result.document
            logger.info(f'✅ Document AI response received for {company} in {processing_time:.2f}s')
            logger.debug(f'📄 Document contains {len(document.pages)} pages, {len(document.entities)} entities')
            kpis = []
            text_pages = []
            entities_processed = 0
            total_pages = len(document.pages)
            if total_pages == 0:
                logger.warning(f'⚠️  Document AI returned 0 pages for {company}')
                raise ValueError('Document AI returned empty document')
            start_page = max(0, int(total_pages * 0.1))
            end_page = int(total_pages * 0.95)
            logger.info(f'📖 Processing pages {start_page}-{end_page} of {total_pages} (optimized range) for {company}')
            for page_idx in range(start_page, min(end_page, total_pages)):
                page = document.pages[page_idx]
                page_text = self.extract_page_text(page)
                text_pages.append(page_text)
                page_entities = 0
                for entity in page.entities:
                    kpi_data = self.process_document_ai_entity(entity, company, ticker, year, page_idx + 1, page_text)
                    if kpi_data:
                        kpis.append(kpi_data)
                        page_entities += 1
                        entities_processed += 1
                if page_entities > 0:
                    logger.debug(f'📊 Page {page_idx + 1}: extracted {page_entities} KPIs')
            logger.info(f'🔍 Document AI extracted {entities_processed} entities, {len(kpis)} valid KPIs from {company}')
            logger.debug(f'🔄 Running fallback extraction for missed KPIs...')
            fallback_kpis = self.fallback_extraction(text_pages, company, ticker, year, start_page)
            if fallback_kpis:
                logger.info(f'📈 Fallback extraction found {len(fallback_kpis)} additional KPIs')
                kpis.extend(fallback_kpis)
            full_text = ' '.join(text_pages)
            logger.debug(f'🤖 Starting Gemini greenwashing analysis for {company}...')
            greenwashing = self.analyze_greenwashing_with_gemini(full_text, kpis, company, ticker, year)
            logger.info(f'✅ Document AI successfully extracted {len(kpis)} total KPIs from {company}')
            return (kpis, greenwashing)
        except gcp_exceptions.PermissionDenied as e:
            logger.critical(f'🚫 Permission denied for {company}: Check service account roles and API enablement')
            logger.critical(f'   Error details: {str(e)}')
            logger.critical(f'   Required roles: Document AI API User, Document AI API Admin')
            self.document_ai_enabled = False
            break
        except gcp_exceptions.NotFound as e:
            logger.critical(f'🔍 Processor not found for {company}: Verify PROCESSOR_ID and LOCATION')
            logger.critical(f'   Processor name: {self.processor_name}')
            logger.critical(f'   Error details: {str(e)}')
            self.document_ai_enabled = False
            break
        except gcp_exceptions.InvalidArgument as e:
            logger.error(f'📄 Invalid request for {company}: Check PDF content/MIME type')
            logger.error(f'   PDF size: {len(pdf_content)} bytes')
            logger.error(f'   Error details: {str(e)}')
            break
        except gcp_exceptions.ResourceExhausted as e:
            logger.warning(f'⏱️  Rate limit exceeded for {company} (attempt {attempt + 1}/{max_retries})')
            logger.warning(f'   Error details: {str(e)}')
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt * 5
                logger.info(f'⏳ Waiting {wait_time}s before retry...')
                time.sleep(wait_time)
                continue
        except gcp_exceptions.InternalServerError as e:
            logger.warning(f'🌐 Transient server error for {company} (attempt {attempt + 1}/{max_retries})')
            logger.warning(f'   Error details: {str(e)}')
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt * 2
                logger.info(f'⏳ Waiting {wait_time}s before retry...')
                time.sleep(wait_time)
                continue
        except gcp_exceptions.DeadlineExceeded as e:
            logger.warning(f'⏰ Request timeout for {company} (attempt {attempt + 1}/{max_retries})')
            logger.warning(f'   Error details: {str(e)}')
            if attempt < max_retries - 1:
                logger.info(f'⏳ Retrying with same timeout...')
                time.sleep(2 ** attempt)
                continue
        except Exception as e:
            logger.error(f'❌ Unexpected Document AI error for {company} (attempt {attempt + 1}/{max_retries})')
            logger.error(f'   Error type: {type(e).__name__}')
            logger.error(f'   Error message: {str(e)}')
            logger.error(f'   Full traceback: {traceback.format_exc()}')
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f'⏳ Retrying in {wait_time}s...')
                time.sleep(wait_time)
                continue
    logger.warning(f'🔄 Document AI failed for {company} after {max_retries} attempts, using fallback')
    return self.fallback_pdf_processing(pdf_content, company, ticker, year)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
