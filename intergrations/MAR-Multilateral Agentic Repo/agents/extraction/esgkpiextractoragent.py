
class ESGKPIExtractorAgent:
    """Agent based on ESGKPIExtractor from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor.py"""
    
    def __init__(self):
        self.name = "ESGKPIExtractorAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract ESG KPIs from PDF reports using Document AI and OpenAI"""
        """Initialize the KPI extractor"""
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us')
        self.processor_id = os.getenv('GOOGLE_DOCUMENT_AI_PROCESSOR_ID')
        self.document_ai_client = None
        if self.project_id and self.processor_id:
            try:
                creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if creds_path and (not os.path.exists(creds_path)):
                    possible_paths = [os.path.join('..', 'credentials.json'), 'credentials.json', os.path.join('..', '..', 'esg_kpi_mvp', 'credentials.json')]
                    for path in possible_paths:
                        if os.path.exists(path):
                            abs_path = os.path.abspath(path)
                            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = abs_path
                            logger.info(f'Found credentials at: {abs_path}')
                            break
                    else:
                        logger.warning(f'Credentials file not found at {creds_path} or relative paths')
                self.document_ai_client = documentai.DocumentProcessorServiceClient()
                self.processor_name = f'projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}'
                logger.info('Document AI client initialized successfully')
            except Exception as e:
                logger.error(f'Failed to initialize Document AI: {e}')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_available = bool(self.openai_api_key)
        if self.openai_available:
            try:
                openai.api_key = self.openai_api_key
                logger.info('OpenAI API key configured successfully')
            except Exception as e:
                logger.warning(f'OpenAI configuration failed: {e}')
                self.openai_available = False
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), db=int(os.getenv('REDIS_DB', 0)), socket_connect_timeout=2, socket_timeout=2)
            self.redis_client.ping()
            logger.info('Redis cache connected successfully')
        except Exception as e:
            logger.warning(f'Redis server not available: {e}')
            try:
                import fakeredis
                self.redis_client = fakeredis.FakeRedis()
                self.redis_client.ping()
                logger.info('Using FakeRedis for caching (testing mode)')
            except (ImportError, Exception) as fake_e:
                logger.warning(f'FakeRedis not available: {fake_e}, caching disabled')
                self.redis_client = None
        self.db_name = os.getenv('DB_NAME', 'esg_kpi.db')
        self.is_sqlite = self.db_name.endswith('.db') or not os.getenv('DB_HOST')
        if self.is_sqlite:
            self.db_config = {'database': self.db_name}
        else:
        self.kpi_patterns = {'carbon_emissions_scope1': {'patterns': ['scope\\s*1.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'direct.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'scope\\s*1.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)'], 'unit': 'mt CO2e', 'category': 'environmental'}, 'carbon_emissions_scope2': {'patterns': ['scope\\s*2.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'indirect.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'scope\\s*2.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)'], 'unit': 'mt CO2e', 'category': 'environmental'}, 'carbon_emissions_scope3': {'patterns': ['scope\\s*3.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'value\\s*chain.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'scope\\s*3.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)'], 'unit': 'mt CO2e', 'category': 'environmental'}, 'water_consumption': {'patterns': ['water.*?consumption.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(million\\s*gallons?|megalit[re]s?|m3)', 'water.*?use.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(million\\s*gallons?|megalit[re]s?|m3)', 'total.*?water.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(million\\s*gallons?|megalit[re]s?|m3)'], 'unit': 'million gallons', 'category': 'environmental'}, 'renewable_energy': {'patterns': ['renewable.*?energy.*?(\\d+(?:\\.\\d+)?)\\s*%', 'clean.*?energy.*?(\\d+(?:\\.\\d+)?)\\s*%', '(\\d+(?:\\.\\d+)?)\\s*%.*?renewable'], 'unit': '%', 'category': 'environmental'}, 'waste_diverted': {'patterns': ['waste.*?diverted.*?(\\d+(?:\\.\\d+)?)\\s*%', 'diversion.*?rate.*?(\\d+(?:\\.\\d+)?)\\s*%', '(\\d+(?:\\.\\d+)?)\\s*%.*?waste.*?diverted'], 'unit': '%', 'category': 'environmental'}, 'diversity_women': {'patterns': ['women.*?workforce.*?(\\d+(?:\\.\\d+)?)\\s*%', 'female.*?employees.*?(\\d+(?:\\.\\d+)?)\\s*%', '(\\d+(?:\\.\\d+)?)\\s*%.*?women'], 'unit': '%', 'category': 'social'}, 'diversity_leadership': {'patterns': ['diverse.*?leadership.*?(\\d+(?:\\.\\d+)?)\\s*%', 'leadership.*?diversity.*?(\\d+(?:\\.\\d+)?)\\s*%', '(\\d+(?:\\.\\d+)?)\\s*%.*?diverse.*?leader'], 'unit': '%', 'category': 'social'}, 'safety_incidents': {'patterns': ['recordable.*?incident.*?rate.*?(\\d+(?:\\.\\d+)?)', 'trir.*?(\\d+(?:\\.\\d+)?)', 'safety.*?incident.*?(\\d+(?:\\.\\d+)?)'], 'unit': 'incidents per 100 employees', 'category': 'social'}, 'board_independence': {'patterns': ['independent.*?director.*?(\\d+(?:\\.\\d+)?)\\s*%', 'board.*?independence.*?(\\d+(?:\\.\\d+)?)\\s*%', '(\\d+(?:\\.\\d+)?)\\s*%.*?independent.*?director'], 'unit': '%', 'category': 'governance'}}
    def get_db_connection(self):
        """Get database connection"""
        if self.is_sqlite:
            return sqlite3.connect(self.db_config['database'])
        else:
            if not POSTGRES_AVAILABLE:
                raise ImportError('PostgreSQL required but psycopg2 not installed')
            return psycopg2.connect(**self.db_config)
    def download_pdf(self, url: str) -> Optional[bytes]:
        """
        Download PDF from URL
        Args:
            url (str): PDF URL
        Returns:
            Optional[bytes]: PDF content or None if failed
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; ESG-Extractor/1.0)', 'Accept': 'application/pdf,*/*'}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            if response.headers.get('content-type', '').lower().startswith('application/pdf') or url.lower().endswith('.pdf'):
                return response.content
            else:
                logger.warning(f"URL {url} doesn't appear to be a PDF")
        except Exception as e:
            logger.error(f'Error downloading PDF from {url}: {e}')
    def extract_text_document_ai(self, pdf_content: bytes) -> Optional[str]:
        """
        Extract text from PDF using Google Document AI with page chunking
        Args:
            pdf_content (bytes): PDF content
        Returns:
            Optional[str]: Extracted text or None if failed
        """
        if not self.document_ai_client:
            logger.warning('Document AI client not available')
        try:
            document = {'content': pdf_content, 'mime_type': 'application/pdf'}
            request = {'name': self.processor_name, 'raw_document': document}
            result = self.document_ai_client.process_document(request=request)
            text = result.document.text
            logger.info(f'Document AI extracted {len(text)} characters from full document')
            return text
        except GoogleAPIError as e:
            if 'PAGE_LIMIT_EXCEEDED' in str(e):
                logger.warning(f'Document exceeds page limit, attempting chunked processing: {e}')
                return self._extract_text_document_ai_chunked(pdf_content)
            else:
                logger.error(f'Google Document AI error: {e}')
        except Exception as e:
            logger.error(f'Error processing document with Document AI: {e}')
    def _extract_text_document_ai_chunked(self, pdf_content: bytes) -> Optional[str]:
        """
        Extract text from large PDF using Document AI with page chunking
        Args:
            pdf_content (bytes): PDF content
        Returns:
            Optional[str]: Extracted text from all chunks combined
        """
        try:
            import PyPDF2
            from io import BytesIO
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            total_pages = len(pdf_reader.pages)
            logger.info(f'Processing {total_pages} pages in chunks of 25 pages')
            all_text = []
            chunk_size = 25
            for start_page in range(0, total_pages, chunk_size):
                end_page = min(start_page + chunk_size, total_pages)
                pdf_writer = PyPDF2.PdfWriter()
                for page_num in range(start_page, end_page):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                chunk_buffer = BytesIO()
                pdf_writer.write(chunk_buffer)
                chunk_content = chunk_buffer.getvalue()
                chunk_buffer.close()
                logger.info(f'Processing pages {start_page + 1}-{end_page} with Document AI')
                document = {'content': chunk_content, 'mime_type': 'application/pdf'}
                request = {'name': self.processor_name, 'raw_document': document}
                result = self.document_ai_client.process_document(request=request)
                chunk_text = result.document.text
                if chunk_text:
                    all_text.append(chunk_text)
                    logger.info(f'Extracted {len(chunk_text)} characters from pages {start_page + 1}-{end_page}')
            combined_text = '\n\n--- PAGE BREAK ---\n\n'.join(all_text)
            logger.info(f'Document AI chunked processing completed: {len(combined_text)} total characters')
            return combined_text
        except Exception as e:
            logger.error(f'Error in chunked Document AI processing: {e}')
    def extract_text_fallback(self, pdf_content: bytes) -> Optional[str]:
        """
        Fallback text extraction using PyPDF2 and pdfplumber
        Args:
            pdf_content (bytes): PDF content
        Returns:
            Optional[str]: Extracted text or None if failed
        """
        try:
            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                if text_parts:
                    extracted_text = '\n'.join(text_parts)
                    logger.info(f'pdfplumber extracted {len(extracted_text)} characters')
                    return extracted_text
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            if text_parts:
                extracted_text = '\n'.join(text_parts)
                logger.info(f'PyPDF2 extracted {len(extracted_text)} characters')
                return extracted_text
        except Exception as e:
            logger.error(f'Error in fallback text extraction: {e}')
    def extract_kpis_regex(self, text: str) -> List[KPIData]:
        """
        Extract KPIs using regex patterns
        Args:
            text (str): Extracted text from PDF
        Returns:
            List[KPIData]: List of extracted KPIs
        """
        kpis = []
        text_clean = re.sub('\\s+', ' ', text.lower())
        year_match = re.search('20(1[0-9]|2[0-9])', text)
        document_year = int(year_match.group()) if year_match else None
        for kpi_name, config in self.kpi_patterns.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, text_clean, re.IGNORECASE)
                for match in matches:
                    try:
                        value_str = match.group(1).replace(',', '')
                        value = float(value_str)
                        unit = config['unit']
                        if len(match.groups()) > 1 and match.group(2):
                            unit = match.group(2)
                        kpi = KPIData(company='', ticker='', kpi_name=kpi_name, kpi_value=value, kpi_unit=unit, kpi_year=document_year, confidence_score=0.7, source_url='', extraction_method='regex', raw_text=match.group(0))
                        kpis.append(kpi)
                    except (ValueError, IndexError) as e:
                        logger.debug(f'Error parsing KPI match: {e}')
                        continue
        return kpis
    def extract_kpis_openai(self, text: str, max_length: int=4000) -> List[KPIData]:
        """
        Extract KPIs using OpenAI GPT for advanced text understanding
        Args:
            text (str): Extracted text from PDF
            max_length (int): Maximum text length to send to OpenAI
        Returns:
            List[KPIData]: List of extracted KPIs
        """
        if not self.openai_available:
            logger.warning('OpenAI API not available')
            return []
        try:
            if len(text) > max_length:
                text = text[:max_length]
            prompt = f'\n            Extract ESG (Environmental, Social, Governance) KPIs from the following text.\n            \n            Look for specific metrics like:\n            - Carbon emissions (Scope 1, 2, 3)\n            - Water consumption\n            - Renewable energy percentage\n            - Waste diversion rate\n            - Diversity metrics (women in workforce, leadership diversity)\n            - Safety incidents\n            - Board independence\n            \n            For each KPI found, provide:\n            - KPI name\n            - Numeric value\n            - Unit (if available)\n            - Year (if mentioned)\n            \n            Format as JSON array with objects containing: name, value, unit, year\n            \n            Text to analyze:\n            {text}\n            \n            JSON output:\n            '
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{'role': 'system', 'content': 'You are an expert ESG analyst extracting KPIs from corporate reports.'}, {'role': 'user', 'content': prompt}], max_tokens=1000, temperature=0.1)
            content = response.choices[0].message.content.strip()
            json_match = re.search('\\[.*?\\]', content, re.DOTALL)
            if json_match:
                kpi_data = json.loads(json_match.group())
                kpis = []
                for item in kpi_data:
                    if 'name' in item and 'value' in item:
                        kpi = KPIData(company='', ticker='', kpi_name=item['name'], kpi_value=float(item['value']) if item['value'] else None, kpi_unit=item.get('unit'), kpi_year=int(item['year']) if item.get('year') else None, confidence_score=0.9, source_url='', extraction_method='openai', raw_text=content)
                        kpis.append(kpi)
                return kpis
            logger.warning('Could not parse OpenAI response as JSON')
            return []
        except Exception as e:
            logger.error(f'Error extracting KPIs with OpenAI: {e}')
            return []
    def process_pdf_url(self, company: str, ticker: str, url: str) -> ExtractionResult:
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
    def _deduplicate_kpis(self, kpis: List[KPIData]) -> List[KPIData]:
        """
        Remove duplicate KPIs, keeping the one with highest confidence
        Args:
            kpis (List[KPIData]): List of KPIs to deduplicate
        Returns:
            List[KPIData]: Deduplicated KPIs
        """
        kpi_dict = {}
        for kpi in kpis:
            key = (kpi.kpi_name, kpi.kpi_value, kpi.kpi_unit)
            if key not in kpi_dict or kpi.confidence_score > kpi_dict[key].confidence_score:
                kpi_dict[key] = kpi
        return list(kpi_dict.values())
    def _save_extraction_result(self, result: ExtractionResult):
        """Save extraction result to database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            if self.is_sqlite:
                cursor.execute('\n                    CREATE TABLE IF NOT EXISTS extracted_kpis (\n                        id INTEGER PRIMARY KEY AUTOINCREMENT,\n                        company TEXT,\n                        ticker TEXT,\n                        kpi_name TEXT,\n                        kpi_value REAL,\n                        kpi_unit TEXT,\n                        kpi_year INTEGER,\n                        confidence_score REAL,\n                        source_url TEXT,\n                        extraction_method TEXT,\n                        raw_text TEXT,\n                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n                    )\n                ')
            else:
                cursor.execute('\n                    CREATE TABLE IF NOT EXISTS extracted_kpis (\n                        id SERIAL PRIMARY KEY,\n                        company VARCHAR(255),\n                        ticker VARCHAR(50),\n                        kpi_name VARCHAR(255),\n                        kpi_value FLOAT,\n                        kpi_unit VARCHAR(100),\n                        kpi_year INTEGER,\n                        confidence_score FLOAT,\n                        source_url TEXT,\n                        extraction_method VARCHAR(50),\n                        raw_text TEXT,\n                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                    )\n                ')
            for kpi in result.kpis_extracted:
                if self.is_sqlite:
                    cursor.execute('\n                        INSERT INTO extracted_kpis \n                        (company, ticker, kpi_name, kpi_value, kpi_unit, kpi_year, \n                         confidence_score, source_url, extraction_method, raw_text)\n                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\n                    ', (kpi.company, kpi.ticker, kpi.kpi_name, kpi.kpi_value, kpi.kpi_unit, kpi.kpi_year, kpi.confidence_score, kpi.source_url, kpi.extraction_method, kpi.raw_text))
                else:
                    cursor.execute('\n                        INSERT INTO extracted_kpis \n                        (company, ticker, kpi_name, kpi_value, kpi_unit, kpi_year, \n                         confidence_score, source_url, extraction_method, raw_text)\n                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\n                    ', (kpi.company, kpi.ticker, kpi.kpi_name, kpi.kpi_value, kpi.kpi_unit, kpi.kpi_year, kpi.confidence_score, kpi.source_url, kpi.extraction_method, kpi.raw_text))
            if self.is_sqlite:
                cursor.execute('\n                    CREATE TABLE IF NOT EXISTS extraction_log (\n                        id INTEGER PRIMARY KEY AUTOINCREMENT,\n                        company TEXT,\n                        ticker TEXT,\n                        source_url TEXT,\n                        kpis_count INTEGER,\n                        processing_time REAL,\n                        success INTEGER,\n                        error_message TEXT,\n                        document_pages INTEGER,\n                        text_length INTEGER,\n                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n                    )\n                ')
                cursor.execute('\n                    INSERT INTO extraction_log \n                    (company, ticker, source_url, kpis_count, processing_time, \n                     success, error_message, document_pages, text_length)\n                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)\n                ', (result.company, result.ticker, result.source_url, len(result.kpis_extracted), result.processing_time, 1 if result.success else 0, result.error_message, result.document_pages, result.text_length))
            else:
                cursor.execute('\n                    CREATE TABLE IF NOT EXISTS extraction_log (\n                        id SERIAL PRIMARY KEY,\n                        company VARCHAR(255),\n                        ticker VARCHAR(50),\n                        source_url TEXT,\n                        kpis_count INTEGER,\n                        processing_time FLOAT,\n                        success BOOLEAN,\n                        error_message TEXT,\n                        document_pages INTEGER,\n                        text_length INTEGER,\n                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                    )\n                ')
                cursor.execute('\n                    INSERT INTO extraction_log \n                    (company, ticker, source_url, kpis_count, processing_time, \n                     success, error_message, document_pages, text_length)\n                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)\n                ', (result.company, result.ticker, result.source_url, len(result.kpis_extracted), result.processing_time, result.success, result.error_message, result.document_pages, result.text_length))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f'Error saving extraction result: {e}')
    def process_company_urls(self, company: str, ticker: str, urls: List[str]) -> List[ExtractionResult]:
        """
        Process all PDF URLs for a company
        Args:
            company (str): Company name
            ticker (str): Stock ticker
            urls (List[str]): List of PDF URLs
        Returns:
            List[ExtractionResult]: Processing results for each URL
        """
        results = []
        for url in urls:
            result = self.process_pdf_url(company, ticker, url)
            results.append(result)
            time.sleep(1)
        return results
    def load_urls_from_database(self) -> List[Dict]:
        """
        Load URLs from ESG scraper results
        Returns:
            List[Dict]: List of company URLs from database
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('\n                SELECT DISTINCT company, ticker, url \n                FROM esg_urls \n                WHERE url IS NOT NULL\n                ORDER BY company\n            ')
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f'Error loading URLs from database: {e}')
            return []
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
