
class DocumentAIKPIExtractorAgent:
    """Agent based on DocumentAIKPIExtractor from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_document_ai.py"""
    
    def __init__(self):
        self.name = "DocumentAIKPIExtractorAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Enhanced KPI Extractor with Document AI and Gemini Pro"""
        """Initialize the Document AI enhanced extractor"""
        self.setup_document_ai()
        self.setup_gemini()
        self.load_greenwashing_config()
        self.kpi_entity_mapping = {'CARBON_EMISSIONS': 'carbon_emissions_scope1', 'SCOPE_1_EMISSIONS': 'carbon_emissions_scope1', 'SCOPE_2_EMISSIONS': 'carbon_emissions_scope2', 'SCOPE_3_EMISSIONS': 'carbon_emissions_scope3', 'RENEWABLE_ENERGY': 'renewable_energy_percentage', 'ENERGY_CONSUMPTION': 'energy_consumption', 'WATER_USAGE': 'water_usage', 'WASTE_RECYCLED': 'waste_recycled_percentage', 'EMPLOYEE_COUNT': 'employee_count', 'DIVERSITY_PERCENTAGE': 'diversity_percentage', 'SAFETY_INCIDENTS': 'safety_incidents', 'BOARD_DIVERSITY': 'board_diversity_percentage'}
        self.fallback_patterns = {'carbon_emissions_scope1': ['scope\\s*1.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'direct.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)'], 'carbon_emissions_scope2': ['scope\\s*2.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'indirect.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)'], 'renewable_energy_percentage': ['renewable.*?energy.*?(\\d+(?:\\.\\d+)?)\\s*%', 'clean.*?energy.*?(\\d+(?:\\.\\d+)?)\\s*%']}
    def setup_document_ai(self):
        """Initialize Document AI client with comprehensive validation"""
        try:
            logger.info('🔧 Initializing Document AI client...')
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')
            if not credentials_path:
                logger.warning('⚠️  GOOGLE_APPLICATION_CREDENTIALS not set, Document AI disabled')
                self.document_ai_enabled = False
                return
            if not os.path.exists(credentials_path):
                logger.warning(f'⚠️  Google Cloud credentials not found at {credentials_path}, Document AI disabled')
                self.document_ai_enabled = False
                return
            try:
                with open(credentials_path, 'r') as f:
                    import json
                    creds_data = json.load(f)
                    if 'type' not in creds_data or creds_data.get('type') != 'service_account':
                        logger.warning('⚠️  Credentials file is not a service account key')
                    logger.debug(f"📋 Service account: {creds_data.get('client_email', 'unknown')}")
            except json.JSONDecodeError as e:
                logger.error(f'❌ Invalid JSON in credentials file: {e}')
                self.document_ai_enabled = False
                return
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            self.doc_ai_client = documentai.DocumentProcessorServiceClient()
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
            location = os.getenv('DOCUMENT_AI_LOCATION', 'us')
            processor_id = os.getenv('DOCUMENT_AI_PROCESSOR_ID')
            if not project_id or project_id == 'your-project-id':
                logger.error('❌ GOOGLE_CLOUD_PROJECT_ID not set or using placeholder value')
                self.document_ai_enabled = False
                return
            if not processor_id or processor_id == 'your-processor-id':
                logger.error('❌ DOCUMENT_AI_PROCESSOR_ID not set or using placeholder value')
                self.document_ai_enabled = False
                return
            self.processor_name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'
            try:
                logger.debug('🧪 Testing Document AI client connectivity...')
                processor = self.doc_ai_client.get_processor(name=self.processor_name)
                logger.info(f'✅ Document AI processor validated: {processor.display_name}')
            except gcp_exceptions.PermissionDenied:
                logger.warning('⚠️  Permission denied accessing processor - check service account roles')
                logger.warning('   Required roles: Document AI API User, Document AI API Admin')
            except gcp_exceptions.NotFound:
                logger.error(f'❌ Processor not found: {self.processor_name}')
                logger.error('   Check DOCUMENT_AI_PROCESSOR_ID and DOCUMENT_AI_LOCATION')
                self.document_ai_enabled = False
                return
            except Exception as e:
                logger.warning(f'⚠️  Could not validate processor (will try during processing): {e}')
            self.document_ai_enabled = True
            logger.info(f'✅ Document AI initialized successfully')
            logger.info(f'   Project: {project_id}')
            logger.info(f'   Location: {location}')
            logger.info(f'   Processor: {processor_id}')
        except Exception as e:
            logger.error(f'❌ Failed to initialize Document AI: {e}')
            logger.error(f'   Full error: {traceback.format_exc()}')
            self.document_ai_enabled = False
    def setup_gemini(self):
        """Initialize Gemini Pro"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.warning('Gemini API key not found, using fallback analysis')
                self.gemini_enabled = False
                return
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini_enabled = True
            logger.info('Gemini Pro initialized successfully')
        except Exception as e:
            logger.error(f'Failed to initialize Gemini Pro: {e}')
            self.gemini_enabled = False
    def load_greenwashing_config(self):
        """Load greenwashing configuration"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'greenwashing_config.json')
            with open(config_path, 'r') as f:
                self.greenwashing_config = json.load(f)
        except Exception as e:
            logger.warning(f'Could not load greenwashing config: {e}')
            self.greenwashing_config = {'indicators': {'vagueness': {'patterns': ['committed to', 'striving for'], 'threshold': 0.05}, 'contradictions': {'zero_claims': ['zero emissions', 'carbon neutral']}, 'sentiment_imbalance': {'positive_threshold': 0.3}}, 'weights': {'vagueness': 0.25, 'contradictions': 0.3, 'sentiment_imbalance': 0.2}, 'thresholds': {'low': 25, 'medium': 50, 'high': 75}}
    def process_pdf_with_document_ai(self, pdf_content: bytes, company: str, ticker: str, year: int) -> Tuple[List[KPIMetadata], GreenwashingAnalysis]:
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
    def extract_page_text(self, page) -> str:
        """Extract text from Document AI page"""
        text_segments = []
        for text_anchor in page.layout.text_anchor.text_segments:
            start_index = text_anchor.start_index
            end_index = text_anchor.end_index
            text_segments.append(page.text[start_index:end_index])
        return ' '.join(text_segments)
    def process_document_ai_entity(self, entity, company: str, ticker: str, year: int, page_num: int, page_text: str) -> Optional[KPIMetadata]:
        """Process a Document AI entity into KPI metadata"""
        try:
            entity_type = entity.type_
            kpi_name = self.kpi_entity_mapping.get(entity_type)
            if not kpi_name:
            mention_text = entity.mention_text
            confidence = entity.confidence
            value_match = re.search('(\\d+[\\d,]*(?:\\.\\d+)?)', mention_text)
            if not value_match:
            kpi_value = float(value_match.group(1).replace(',', ''))
            unit_match = re.search('(mt|tonnes?|tons?|tco2e?|%|kwh|mwh|gwh)', mention_text.lower())
            kpi_unit = unit_match.group(1) if unit_match else self.get_default_unit(kpi_name)
            context_start = max(0, page_text.find(mention_text) - 100)
            context_end = min(len(page_text), page_text.find(mention_text) + len(mention_text) + 100)
            context_text = page_text[context_start:context_end]
            return KPIMetadata(company=company, ticker=ticker, kpi_name=kpi_name, kpi_value=kpi_value, kpi_unit=kpi_unit, kpi_year=year, confidence_score=confidence, source_url='', extraction_method='document_ai', report_name='', page_number=page_num, matched_text=mention_text, context_text=context_text, created_at=datetime.now())
        except Exception as e:
            logger.warning(f'Failed to process entity: {e}')
    def fallback_extraction(self, text_pages: List[str], company: str, ticker: str, year: int, start_page: int) -> List[KPIMetadata]:
        """Fallback regex extraction for missed KPIs"""
        kpis = []
        for page_idx, page_text in enumerate(text_pages):
            page_num = start_page + page_idx + 1
            for kpi_name, patterns in self.fallback_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, page_text, re.IGNORECASE)
                    for match in matches:
                        try:
                            value_str = match.group(1).replace(',', '')
                            kpi_value = float(value_str)
                            kpi_unit = match.group(2) if len(match.groups()) > 1 else self.get_default_unit(kpi_name)
                            start_pos = max(0, match.start() - 100)
                            end_pos = min(len(page_text), match.end() + 100)
                            context_text = page_text[start_pos:end_pos]
                            kpi = KPIMetadata(company=company, ticker=ticker, kpi_name=kpi_name, kpi_value=kpi_value, kpi_unit=kpi_unit, kpi_year=year, confidence_score=0.75, source_url='', extraction_method='regex_fallback', report_name='', page_number=page_num, matched_text=match.group(0), context_text=context_text, created_at=datetime.now())
                            kpis.append(kpi)
                        except (ValueError, IndexError):
                            continue
        return kpis
    def analyze_greenwashing_with_gemini(self, text: str, kpis: List[KPIMetadata], company: str, ticker: str, year: int) -> GreenwashingAnalysis:
        """Analyze greenwashing using Gemini Pro"""
        if not self.gemini_enabled:
            return self.fallback_greenwashing_analysis(text, company, ticker, year)
        try:
            kpi_summary = [{'name': kpi.kpi_name, 'value': kpi.kpi_value, 'confidence': kpi.confidence_score} for kpi in kpis[:10]]
            prompt = f'\n            Analyze the following ESG report text for greenwashing indicators. Return a JSON response with the following structure:\n            {{\n                "overall_score": <0-100 score where 100 is high greenwashing risk>,\n                "indicator_scores": {{\n                    "vagueness": <0-100>,\n                    "contradictions": <0-100>,\n                    "sentiment_imbalance": <0-100>,\n                    "omissions": <0-100>,\n                    "hype": <0-100>\n                }},\n                "flagged_sections": [\n                    {{"text": "concerning text", "reason": "vague commitment", "score": 75}}\n                ]\n            }}\n            \n            Company: {company}\n            Year: {year}\n            KPIs Found: {json.dumps(kpi_summary)}\n            \n            Text to analyze (first 2000 chars): {text[:2000]}\n            \n            Focus on:\n            1. Vague commitments ("striving for", "committed to")\n            2. Contradictions between claims and data\n            3. Sentiment imbalance (too positive, hiding risks)\n            4. Missing scope 3 emissions or governance details\n            5. Hyperbolic language without substance\n            '
            response = self.gemini_model.generate_content(prompt)
            try:
                response_text = response.text
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end]
                    gemini_result = json.loads(json_str)
                    return GreenwashingAnalysis(company=company, ticker=ticker, overall_score=gemini_result.get('overall_score', 0), indicator_scores=gemini_result.get('indicator_scores', {}), flagged_sections=gemini_result.get('flagged_sections', []), report_name=f'{company}_ESG_Report_{year}', analysis_year=year, analysis_date=datetime.now())
                else:
                    raise ValueError('No JSON found in Gemini response')
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f'Failed to parse Gemini response: {e}')
                return self.fallback_greenwashing_analysis(text, company, ticker, year)
        except Exception as e:
            logger.error(f'Gemini analysis failed: {e}')
            return self.fallback_greenwashing_analysis(text, company, ticker, year)
    def fallback_greenwashing_analysis(self, text: str, company: str, ticker: str, year: int) -> GreenwashingAnalysis:
        """Fallback greenwashing analysis using traditional methods"""
        vagueness_score = len(re.findall('committed to|striving for|working towards', text, re.IGNORECASE)) * 20
        contradiction_score = len(re.findall('zero emissions|carbon neutral|net zero', text, re.IGNORECASE)) * 25
        overall_score = min(100, (vagueness_score + contradiction_score) / 2)
        return GreenwashingAnalysis(company=company, ticker=ticker, overall_score=overall_score, indicator_scores={'vagueness': min(100, vagueness_score), 'contradictions': min(100, contradiction_score), 'sentiment_imbalance': 0, 'omissions': 0, 'hype': 0}, flagged_sections=[], report_name=f'{company}_ESG_Report_{year}', analysis_year=year, analysis_date=datetime.now())
    def fallback_pdf_processing(self, pdf_content: bytes, company: str, ticker: str, year: int) -> Tuple[List[KPIMetadata], GreenwashingAnalysis]:
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
    def get_default_unit(self, kpi_name: str) -> str:
        """Get default unit for KPI"""
        unit_mapping = {'carbon_emissions_scope1': 'mt CO2e', 'carbon_emissions_scope2': 'mt CO2e', 'carbon_emissions_scope3': 'mt CO2e', 'renewable_energy_percentage': '%', 'energy_consumption': 'MWh', 'water_usage': 'megalitres', 'waste_recycled_percentage': '%', 'employee_count': 'count', 'diversity_percentage': '%', 'safety_incidents': 'count', 'board_diversity_percentage': '%'}
        return unit_mapping.get(kpi_name, 'units')
    def process_pdf_with_metadata(self, pdf_url: str, company: str, ticker: str, year: int=None) -> Tuple[List[KPIMetadata], GreenwashingAnalysis]:
        """Main processing method with Document AI"""
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            pdf_content = response.content
            resolved_year = year or self.extract_year_from_context(pdf_content) or 2024
            if self.document_ai_enabled:
                return self.process_pdf_with_document_ai(pdf_content, company, ticker, resolved_year)
            else:
                return self.fallback_pdf_processing(pdf_content, company, ticker, resolved_year)
        except Exception as e:
            logger.error(f'Failed to process PDF {pdf_url}: {e}')
            return ([], self.fallback_greenwashing_analysis('', company, ticker, year or 2024))
    def extract_year_from_context(self, pdf_content: bytes) -> Optional[int]:
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
    def save_results_to_database(self, kpis: List[KPIMetadata], greenwashing: GreenwashingAnalysis):
        """Save results to database"""
        try:
            if kpis:
                kpi_df = pd.DataFrame([asdict(kpi) for kpi in kpis])
                kpi_df.to_sql('extracted_kpis_enhanced', self.engine, if_exists='append', index=False)
                logger.info(f'Saved {len(kpis)} KPIs to database')
            if greenwashing:
                gw_data = {'company': greenwashing.company, 'ticker': greenwashing.ticker, 'overall_score': greenwashing.overall_score, 'indicator_scores': json.dumps(greenwashing.indicator_scores), 'flagged_sections': json.dumps(greenwashing.flagged_sections), 'report_name': greenwashing.report_name, 'analysis_year': greenwashing.analysis_year, 'analysis_date': greenwashing.analysis_date}
                gw_df = pd.DataFrame([gw_data])
                gw_df.to_sql('greenwashing_analysis', self.engine, if_exists='append', index=False)
                logger.info(f'Saved greenwashing analysis for {greenwashing.company}')
        except Exception as e:
            logger.error(f'Failed to save to database: {e}')
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
