
class ESGURLScraperPatchedAgent:
    """Agent based on ESGURLScraperPatched from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\esg_scraper_patched.py"""
    
    def __init__(self):
        self.name = "ESGURLScraperPatchedAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Enhanced ESG URL Scraper with validation fixes and improved hit rates"""
        """
        Initialize the patched ESG URL scraper.
        Args:
            api_key (str): Google API key for Custom Search
            cse_id (str): Google Custom Search Engine ID
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.cse_id = cse_id or os.getenv('GOOGLE_CSE_ID')
        self.search_service = None
        if self.api_key and self.cse_id:
            try:
                self.search_service = build('customsearch', 'v1', developerKey=self.api_key)
                logger.info('Google Custom Search API initialized successfully')
            except Exception as e:
                logger.error(f'Failed to initialize Google Custom Search API: {e}')
        self.redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), db=int(os.getenv('REDIS_DB', 0)))
        self.enhanced_search_queries = ['ESG report filetype:pdf', 'sustainability report filetype:pdf', 'environmental social governance filetype:pdf', 'CSR report filetype:pdf', 'sustainability disclosure filetype:pdf', 'corporate responsibility report filetype:pdf', 'environmental report filetype:pdf', 'social responsibility report filetype:pdf', 'governance report filetype:pdf', 'annual sustainability report filetype:pdf', 'annual ESG report filetype:pdf', 'annual corporate responsibility report filetype:pdf', 'citizenship report filetype:pdf', 'impact report filetype:pdf', 'responsible business report filetype:pdf']
        self.company_specific_queries = {'apple': ['environmental progress report filetype:pdf', 'environmental responsibility report filetype:pdf', 'carbon neutral filetype:pdf'], 'tesla': ['impact report filetype:pdf', 'sustainability update filetype:pdf', 'environmental impact filetype:pdf'], 'microsoft': ['sustainability report filetype:pdf', 'environmental sustainability filetype:pdf', 'carbon negative filetype:pdf']}
        self.api_delay = 0.1
        self.retry_delay = 2.0
        self.max_retries = 3
        self.rate_limit_delay = 60
        self.metrics = ScrapingMetrics(0, 0, 0, 0, 0.0, 0, 0, 0.0)
    def normalize_url(self, url: str, preserve_params: bool=True) -> str:
        """
        Normalize URL using urllib.parse - fixes validation issues.
        Args:
            url (str): URL to normalize
            preserve_params (bool): Whether to preserve URL parameters
        Returns:
            str: Normalized URL
        """
        try:
            parsed = urlparse(url)
            if preserve_params:
                normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, ''))
            else:
                normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
            return normalized
        except Exception as e:
            logger.warning(f'URL normalization failed for {url}: {e}')
            return url
    def _is_valid_pdf_url(self, url: str) -> bool:
        """
        Enhanced PDF URL validation with better fragment/parameter handling.
        Args:
            url (str): URL to validate
        Returns:
            bool: True if valid PDF URL
        """
        try:
            normalized_url = self.normalize_url(url)
            parsed = urlparse(normalized_url)
            if not parsed.scheme or not parsed.netloc:
                return False
            if parsed.scheme not in ['http', 'https']:
                return False
            if normalized_url.lower().endswith('.pdf'):
                return True
            if '/pdf/' in normalized_url.lower() or '.pdf?' in normalized_url.lower():
                return True
            if 'pdf' in parsed.query.lower() or 'format=pdf' in parsed.query.lower():
                return True
            return False
        except Exception as e:
            logger.warning(f'PDF URL validation failed for {url}: {e}')
            return False
    def _is_esg_related_url(self, url: str) -> bool:
        """
        Enhanced ESG-related URL detection with more keywords.
        Args:
            url (str): URL to check
        Returns:
            bool: True if URL appears to be ESG-related
        """
        esg_keywords = ['esg', 'sustainability', 'environmental', 'social', 'governance', 'csr', 'corporate-responsibility', 'responsible', 'citizenship', 'impact', 'carbon', 'climate', 'diversity', 'ethics']
        url_lower = url.lower()
        return any((keyword in url_lower for keyword in esg_keywords))
    def search_esg_reports_api_with_retry(self, company: str, website: str, max_results: int=10) -> SearchResult:
        """
        Search for ESG reports using Google Custom Search API with retry logic.
        Args:
            company (str): Company name
            website (str): Company website  
            max_results (int): Maximum number of results
        Returns:
            SearchResult: Search results with metadata
        """
        start_time = time.time()
        retry_count = 0
        cache_key = f'esg_api_patched:{company}:{website}'
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            logger.info(f'API cache hit for {company}')
            cached_data = json.loads(cached_result)
            return SearchResult(**cached_data)
        if not self.search_service:
            return SearchResult(company=company, ticker='', website=website, urls=[], normalized_urls=[], search_method='api', search_time=time.time() - start_time, success=False, error_message='Google Custom Search API not available')
        company_lower = company.lower()
        search_queries = self.enhanced_search_queries.copy()
        for key, queries in self.company_specific_queries.items():
            if key in company_lower:
                search_queries.extend(queries)
                logger.info(f'Added {len(queries)} company-specific queries for {company}')
        all_urls = []
        normalized_urls = []
        while retry_count <= self.max_retries:
            try:
                for query_template in search_queries[:5]:
                    query = f'site:{website} ({query_template})'
                    logger.info(f'API search (attempt {retry_count + 1}): {query}')
                    result = self.search_service.cse().list(q=query, cx=self.cse_id, num=min(max_results, 10), fileType='pdf').execute()
                    self.metrics.api_calls_made += 1
                    for item in result.get('items', []):
                        original_url = item.get('link')
                        if original_url:
                            normalized_url = self.normalize_url(original_url)
                            if self._is_valid_pdf_url(normalized_url) and self._is_esg_related_url(normalized_url):
                                all_urls.append(original_url)
                                normalized_urls.append(normalized_url)
                    time.sleep(self.api_delay)
                    if len(all_urls) >= max_results:
                        break
                seen = set()
                unique_urls = []
                unique_normalized = []
                for i, url in enumerate(all_urls):
                    normalized = normalized_urls[i] if i < len(normalized_urls) else url
                    if normalized not in seen:
                        seen.add(normalized)
                        unique_urls.append(url)
                        unique_normalized.append(normalized)
                search_result = SearchResult(company=company, ticker='', website=website, urls=unique_urls[:max_results], normalized_urls=unique_normalized[:max_results], search_method='api', search_time=time.time() - start_time, success=True, retry_count=retry_count)
                self.redis_client.setex(cache_key, 86400, json.dumps(asdict(search_result)))
                self.metrics.cost_estimate += 0.005 * min(len(search_queries), 5)
                logger.info(f'API search successful for {company}: {len(unique_urls)} URLs found (attempt {retry_count + 1})')
                return search_result
            except HttpError as e:
                if e.resp.status in [429, 403]:
                    retry_count += 1
                    self.metrics.retry_attempts += 1
                    if retry_count <= self.max_retries:
                        delay = self.rate_limit_delay * 2 ** (retry_count - 1)
                        logger.warning(f'Rate limit hit for {company}, retrying in {delay}s (attempt {retry_count})')
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f'Max retries exceeded for {company}: {e}')
                        break
                else:
                    logger.error(f'API error for {company}: {e}')
                    break
            except Exception as e:
                retry_count += 1
                self.metrics.retry_attempts += 1
                if retry_count <= self.max_retries:
                    logger.warning(f'Error searching for {company}, retrying: {e}')
                    time.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(f'Max retries exceeded for {company}: {e}')
                    break
        return SearchResult(company=company, ticker='', website=website, urls=[], normalized_urls=[], search_method='api', search_time=time.time() - start_time, success=False, retry_count=retry_count, error_message=f'Failed after {retry_count} attempts')
    def scrape_company_batch(self, companies_df: pd.DataFrame, max_results: int=5) -> Tuple[List[SearchResult], ScrapingMetrics]:
        """
        Scrape ESG URLs for a batch of companies with enhanced error handling.
        Args:
            companies_df (pd.DataFrame): DataFrame with company information
            max_results (int): Maximum URLs per company
        Returns:
            Tuple[List[SearchResult], ScrapingMetrics]: Results and metrics
        """
        start_time = time.time()
        results = []
        self.metrics.total_companies = len(companies_df)
        for index, row in companies_df.iterrows():
            company = row.get('company', row.get('name', ''))
            website = row.get('website', row.get('url', ''))
            if not company or not website:
                logger.warning(f'Missing data for row {index}: company={company}, website={website}')
                continue
            logger.info(f'Processing {company} ({index + 1}/{len(companies_df)})')
            result = self.search_esg_reports_api_with_retry(company, website, max_results)
            results.append(result)
            if result.success:
                self.metrics.successful_searches += 1
                self.metrics.total_urls_found += len(result.urls)
            else:
                self.metrics.failed_searches += 1
        self.metrics.total_time = time.time() - start_time
        logger.info(f'Batch processing complete: {self.metrics.successful_searches}/{self.metrics.total_companies} successful')
        return (results, self.metrics)
    def save_results_to_database(self, results: List[SearchResult]):
        """
        Save results to database with enhanced schema.
        Args:
            results (List[SearchResult]): Search results to save
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS esg_urls_patched (\n                    id SERIAL PRIMARY KEY,\n                    company VARCHAR(255),\n                    ticker VARCHAR(50),\n                    website VARCHAR(500),\n                    original_url TEXT,\n                    normalized_url TEXT,\n                    search_method VARCHAR(50),\n                    search_time FLOAT,\n                    retry_count INTEGER,\n                    success BOOLEAN,\n                    error_message TEXT,\n                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                )\n            ')
            for result in results:
                for i, url in enumerate(result.urls):
                    normalized_url = result.normalized_urls[i] if i < len(result.normalized_urls) else url
                    cursor.execute('\n                        INSERT INTO esg_urls_patched \n                        (company, ticker, website, original_url, normalized_url, search_method, \n                         search_time, retry_count, success, error_message)\n                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\n                    ', (result.company, result.ticker, result.website, url, normalized_url, result.search_method, result.search_time, result.retry_count, result.success, result.error_message))
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f'Saved {len(results)} results to database')
        except Exception as e:
            logger.error(f'Error saving results to database: {e}')
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
