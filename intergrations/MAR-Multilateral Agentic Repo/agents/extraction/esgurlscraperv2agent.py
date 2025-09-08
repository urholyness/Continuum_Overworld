
class ESGURLScraperV2Agent:
    """Agent based on ESGURLScraperV2 from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\esg_scraper_v2.py"""
    
    def __init__(self):
        self.name = "ESGURLScraperV2Agent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
                """
        Initialize the enhanced ESG URL scraper.
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
        self.redis_available = False
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), db=int(os.getenv('REDIS_DB', 0)), socket_connect_timeout=1)
            self.redis_client.ping()
            self.redis_available = True
            logger.info('Redis cache initialized successfully')
        except Exception as e:
            logger.warning(f'Redis not available, proceeding without cache: {e}')
            self.redis_client = None
        self.db_available = False
        try:
            test_conn = self.get_db_connection()
            if test_conn:
                test_conn.close()
                self.db_available = True
                logger.info('Database connection successful')
        except Exception as e:
            logger.warning(f'Database not available, will continue without saving: {e}')
            self.db_available = False
        self.metrics = ScrapingMetrics(0, 0, 0, 0, 0.0, 0, 0.0)
        self.search_queries = ['ESG report filetype:pdf', 'sustainability report filetype:pdf', 'environmental social governance filetype:pdf', 'corporate sustainability filetype:pdf', 'annual sustainability report filetype:pdf']
        self.api_delay = 0.1
        self.fallback_delay = 2.0
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    def search_esg_reports_api(self, company: str, website: str, max_results: int=10) -> SearchResult:
        """
        Search for ESG reports using Google Custom Search API (primary method).
        Args:
            company (str): Company name
            website (str): Company website
            max_results (int): Maximum number of results
        Returns:
            SearchResult: Search results with metadata
        """
        start_time = time.time()
        cache_key = f'esg_api_v2:{company}:{website}'
        cached_result = None
        if self.redis_available and self.redis_client:
            try:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    logger.info(f'API cache hit for {company}')
                    cached_data = json.loads(cached_result)
                    return SearchResult(**cached_data)
            except Exception as e:
                logger.warning(f'Redis cache error: {e}')
                self.redis_available = False
        if not self.search_service:
            return SearchResult(company=company, ticker='', website=website, urls=[], search_method='api', search_time=time.time() - start_time, success=False, error_message='Google Custom Search API not available')
        all_urls = []
        try:
            for query_template in self.search_queries[:3]:
                query = f'site:{website} {query_template}'
                logger.info(f'API search: {query}')
                result = self.search_service.cse().list(q=query, cx=self.cse_id, num=min(max_results, 10), fileType='pdf').execute()
                self.metrics.api_calls_made += 1
                for item in result.get('items', []):
                    url = item.get('link')
                    if url and self._is_valid_pdf_url(url) and self._is_esg_related_url(url):
                        all_urls.append(url)
                time.sleep(self.api_delay)
                if len(all_urls) >= max_results:
                    break
            seen = set()
            url_scores = []
            for url in all_urls:
                if url not in seen:
                    seen.add(url)
                    score = self._score_esg_url(url)
                    url_scores.append((url, score))
            url_scores.sort(key=lambda x: x[1], reverse=True)
            unique_urls = [url for url, score in url_scores]
            search_result = SearchResult(company=company, ticker='', website=website, urls=unique_urls[:max_results], search_method='api', search_time=time.time() - start_time, success=True)
            if self.redis_available and self.redis_client:
                try:
                    self.redis_client.setex(cache_key, 86400, json.dumps(asdict(search_result)))
                except Exception as e:
                    logger.warning(f'Redis cache write error: {e}')
                    self.redis_available = False
            self.metrics.cost_estimate += 0.005 * len(self.search_queries[:3])
            logger.info(f'API search successful for {company}: {len(unique_urls)} URLs found')
            return search_result
        except HttpError as e:
            error_msg = f'Google API error: {e}'
            logger.error(f'API search failed for {company}: {error_msg}')
            return SearchResult(company=company, ticker='', website=website, urls=[], search_method='api', search_time=time.time() - start_time, success=False, error_message=error_msg)
        except Exception as e:
            error_msg = f'Unexpected error: {e}'
            logger.error(f'API search failed for {company}: {error_msg}')
            return SearchResult(company=company, ticker='', website=website, urls=[], search_method='api', search_time=time.time() - start_time, success=False, error_message=error_msg)
    def search_esg_reports_fallback(self, company: str, website: str, max_results: int=5) -> SearchResult:
        """
        Fallback search method using direct web scraping (when API fails).
        Args:
            company (str): Company name
            website (str): Company website
            max_results (int): Maximum number of results
        Returns:
            SearchResult: Search results with metadata
        """
        start_time = time.time()
        cache_key = f'esg_fallback_v2:{company}:{website}'
        cached_result = None
        if self.redis_available and self.redis_client:
            try:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    logger.info(f'Fallback cache hit for {company}')
                    cached_data = json.loads(cached_result)
                    return SearchResult(**cached_data)
            except Exception as e:
                logger.warning(f'Redis cache error: {e}')
                self.redis_available = False
        try:
            raw_urls = self._scrape_company_website(website, max_results * 2)
            url_scores = [(url, self._score_esg_url(url)) for url in raw_urls]
            url_scores.sort(key=lambda x: x[1], reverse=True)
            urls = [url for url, score in url_scores[:max_results]]
            search_result = SearchResult(company=company, ticker='', website=website, urls=urls, search_method='fallback', search_time=time.time() - start_time, success=len(urls) > 0)
            if self.redis_available and self.redis_client:
                try:
                    self.redis_client.setex(cache_key, 21600, json.dumps(asdict(search_result)))
                except Exception as e:
                    logger.warning(f'Redis cache write error: {e}')
                    self.redis_available = False
            logger.info(f'Fallback search for {company}: {len(urls)} URLs found')
            return search_result
        except Exception as e:
            error_msg = f'Fallback search error: {e}'
            logger.error(f'Fallback search failed for {company}: {error_msg}')
            return SearchResult(company=company, ticker='', website=website, urls=[], search_method='fallback', search_time=time.time() - start_time, success=False, error_message=error_msg)
    def _scrape_company_website(self, website: str, max_results: int=5) -> List[str]:
        """
        Scrape company website for ESG/sustainability reports.
        Args:
            website (str): Company website domain
            max_results (int): Maximum URLs to find
        Returns:
            List[str]: List of PDF URLs found
        """
        urls = []
        try:
            common_paths = ['/sustainability', '/esg', '/corporate-responsibility', '/investors', '/about/sustainability', '/our-impact', '/responsibility']
            base_url = f'https://{website}'
            for path in common_paths:
                try:
                    full_url = f'{base_url}{path}'
                    response = requests.get(full_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0 (compatible; ESG-Scraper/1.0)'})
                    if response.status_code == 200:
                        import re
                        pdf_links = re.findall('href=["\\\'](.*?\\.pdf)["\\\']', response.text, re.IGNORECASE)
                        for link in pdf_links:
                            if not link.startswith('http'):
                                link = urljoin(full_url, link)
                            if self._is_esg_related_url(link):
                                urls.append(link)
                                if len(urls) >= max_results:
                                    break
                    time.sleep(0.5)
                except Exception as e:
                    logger.debug(f'Failed to scrape {full_url}: {e}')
                    continue
                if len(urls) >= max_results:
                    break
        except Exception as e:
            logger.error(f'Website scraping failed for {website}: {e}')
        return urls
    def _is_esg_related_url(self, url: str) -> bool:
        """Check if URL is likely an ESG-related document"""
        url_lower = url.lower()
        esg_keywords = ['sustainability', 'esg', 'environmental', 'social', 'governance', 'corporate-responsibility', 'csr', 'impact', 'annual-report', 'sustainability-report', 'corporate-social-responsibility', 'environmental-report', 'climate-change', 'carbon', 'diversity', 'inclusion', 'ethics', 'responsible', 'green-report', 'sustainable-development', 'sdg', 'stakeholder', 'transparency', 'citizenship']
        return any((keyword in url_lower for keyword in esg_keywords))
    def _score_esg_url(self, url: str) -> int:
        """Score ESG URLs by relevance (higher = better)"""
        url_lower = url.lower()
        score = 0
        high_priority = ['sustainability-report', 'esg-report', 'esg', 'sustainability']
        for keyword in high_priority:
            if keyword in url_lower:
                score += 3
        medium_priority = ['corporate-responsibility', 'csr', 'environmental', 'social', 'governance']
        for keyword in medium_priority:
            if keyword in url_lower:
                score += 2
        low_priority = ['annual-report', 'impact', 'climate', 'carbon', 'diversity']
        for keyword in low_priority:
            if keyword in url_lower:
                score += 1
        import re
        years = re.findall('20(2[0-4]|1[5-9])', url_lower)
        if years:
            latest_year = max((int('20' + year) for year in years))
            if latest_year >= 2020:
                score += 3
            elif latest_year >= 2017:
                score += 2
            else:
                score += 1
        return score
    def _is_valid_pdf_url(self, url: str) -> bool:
        """
        Enhanced PDF URL validation.
        Args:
            url (str): URL to validate
        Returns:
            bool: True if valid PDF URL
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            if url.lower().endswith('.pdf'):
                return True
            try:
                response = requests.head(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0 (compatible; ESG-Scraper/1.0)'})
                content_type = response.headers.get('content-type', '').lower()
                return 'pdf' in content_type
            except:
                return 'pdf' in url.lower()
        except Exception:
            return False
    def scrape_company(self, company: str, ticker: str, website: str) -> SearchResult:
        """
        Scrape ESG URLs for a single company using API-first approach.
        Args:
            company (str): Company name
            ticker (str): Stock ticker
            website (str): Company website
        Returns:
            SearchResult: Search results with metadata
        """
        logger.info(f'Scraping {company} ({ticker}) - {website}')
        result = self.search_esg_reports_api(company, website)
        result.ticker = ticker
        if not result.success or len(result.urls) == 0:
            logger.info(f'Falling back to direct scraping for {company}')
            fallback_result = self.search_esg_reports_fallback(company, website)
            fallback_result.ticker = ticker
            if fallback_result.success and len(fallback_result.urls) > 0:
                result = fallback_result
        if result.success:
            self.metrics.successful_searches += 1
            self.metrics.total_urls_found += len(result.urls)
        else:
            self.metrics.failed_searches += 1
        self.metrics.total_time += result.search_time
        if self.db_available:
            try:
                self._save_search_result(result)
            except Exception as e:
                logger.warning(f'Database save failed (continuing without DB): {e}')
                self.db_available = False
        return result
    def _save_search_result(self, result: SearchResult):
        """Save search result to database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS esg_search_results (\n                    id SERIAL PRIMARY KEY,\n                    company VARCHAR(255),\n                    ticker VARCHAR(50),\n                    website VARCHAR(255),\n                    urls_found INTEGER,\n                    search_method VARCHAR(50),\n                    search_time FLOAT,\n                    success BOOLEAN,\n                    error_message TEXT,\n                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                )\n            ')
            cursor.execute('\n                INSERT INTO esg_search_results \n                (company, ticker, website, urls_found, search_method, search_time, success, error_message)\n                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)\n            ', (result.company, result.ticker, result.website, len(result.urls), result.search_method, result.search_time, result.success, result.error_message))
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS esg_urls (\n                    id SERIAL PRIMARY KEY,\n                    company VARCHAR(255),\n                    ticker VARCHAR(50),\n                    url TEXT,\n                    search_method VARCHAR(50),\n                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                )\n            ')
            for url in result.urls:
                cursor.execute('\n                    INSERT INTO esg_urls (company, ticker, url, search_method)\n                    VALUES (%s, %s, %s, %s)\n                    ON CONFLICT DO NOTHING\n                ', (result.company, result.ticker, url, result.search_method))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f'Error saving search result: {e}')
    def load_companies_from_csv(self, csv_path: str) -> List[Dict[str, str]]:
        """Load companies from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            companies = df.to_dict('records')
            logger.info(f'Loaded {len(companies)} companies from CSV')
            return companies
        except Exception as e:
            logger.error(f'Error loading companies from CSV: {e}')
            return []
    def scrape_all_companies(self, csv_path: str, max_companies: Optional[int]=None) -> Tuple[List[SearchResult], ScrapingMetrics]:
        """
        Scrape ESG URLs for all companies in CSV file.
        Args:
            csv_path (str): Path to companies CSV file
            max_companies (Optional[int]): Maximum number of companies to process
        Returns:
            Tuple[List[SearchResult], ScrapingMetrics]: Results and metrics
        """
        companies = self.load_companies_from_csv(csv_path)
        if max_companies:
            companies = companies[:max_companies]
        self.metrics.total_companies = len(companies)
        results = []
        start_time = time.time()
        for i, company_data in enumerate(companies, 1):
            company = company_data['company']
            ticker = company_data['ticker']
            website = company_data['website']
            logger.info(f'Processing {i}/{len(companies)}: {company}')
            result = self.scrape_company(company, ticker, website)
            results.append(result)
            if i % 10 == 0:
                self._log_progress(i, len(companies))
        self.metrics.total_time = time.time() - start_time
        self._save_results_to_csv(results)
        return (results, self.metrics)
    def _log_progress(self, current: int, total: int):
        """Log progress update"""
        success_rate = self.metrics.successful_searches / current * 100
        avg_time = self.metrics.total_time / current
        logger.info(f'Progress: {current}/{total} companies processed')
        logger.info(f'Success rate: {success_rate:.1f}%')
        logger.info(f'Average time per company: {avg_time:.2f}s')
        logger.info(f'Total URLs found: {self.metrics.total_urls_found}')
        logger.info(f'Estimated cost: ${self.metrics.cost_estimate:.2f}')
    def _save_results_to_csv(self, results: List[SearchResult]):
        """Save results to CSV file"""
        try:
            df_data = []
            for result in results:
                df_data.append({'company': result.company, 'ticker': result.ticker, 'website': result.website, 'urls_found': len(result.urls), 'search_method': result.search_method, 'search_time': result.search_time, 'success': result.success, 'urls': '|'.join(result.urls), 'error_message': result.error_message})
            df = pd.DataFrame(df_data)
            output_path = 'data/esg_scraping_results_v2.csv'
            df.to_csv(output_path, index=False)
            logger.info(f'Results saved to {output_path}')
        except Exception as e:
            logger.error(f'Error saving results to CSV: {e}')
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
