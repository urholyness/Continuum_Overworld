
class ESGURLScraperAgent:
    """Agent based on ESGURLScraper from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\scrape_esg_urls.py"""
    
    def __init__(self):
        self.name = "ESGURLScraperAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
                """
        Initialize the ESG URL scraper.
        Args:
            use_custom_search (bool): Whether to use Google Custom Search API
        """
        self.use_custom_search = use_custom_search
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        if use_custom_search:
            from googleapiclient.discovery import build
            self.api_key = os.getenv('GOOGLE_API_KEY')
            self.cse_id = os.getenv('GOOGLE_CSE_ID')
            if not self.api_key or not self.cse_id:
                raise ValueError('Google API key and CSE ID required for Custom Search')
            self.service = build('customsearch', 'v1', developerKey=self.api_key)
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    def search_esg_reports_free(self, company: str, website: str, years: str='2024', max_results: int=5) -> List[Dict[str, str]]:
        """
        Search for ESG reports using free googlesearch-python library with year-based queries.
        Args:
            company (str): Company name
            website (str): Company website
            years (str): Comma-separated years (e.g., "2023,2024")
            max_results (int): Maximum number of results to return per year
        Returns:
            List[Dict[str, str]]: List of dictionaries with URL and year
        """
        try:
            years_list = years.split(',') if years else ['2024']
            all_urls = []
            for year in years_list:
                year = year.strip()
                cache_key = f'esg_urls:{company}:{website}:{year}'
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    logger.info(f'Cache hit for {company} year {year}')
                    cached_urls = json.loads(cached_result)
                    all_urls.extend([{'url': url, 'year': year} for url in cached_urls])
                    continue
                queries = [f'site:{website} ESG report {year} filetype:pdf', f'site:{website} sustainability report {year} filetype:pdf', f'site:{website} environmental social governance {year} filetype:pdf', f'site:{website} corporate responsibility {year} filetype:pdf']
                year_urls = []
                for query in queries:
                    try:
                        logger.info(f'Searching: {query}')
                        search_results = list(search(query, num_results=max_results, sleep_interval=1))
                        year_urls.extend(search_results)
                        time.sleep(2)
                    except Exception as e:
                        logger.warning(f"Search failed for query '{query}': {e}")
                        continue
                unique_urls = list(set(year_urls))
                valid_urls = [url for url in unique_urls if self._is_valid_pdf_url(url)]
                self.redis_client.setex(cache_key, 86400, json.dumps(valid_urls))
                for url in valid_urls[:max_results]:
                    all_urls.append({'url': url, 'year': year})
                logger.info(f'Found {len(valid_urls)} valid ESG URLs for {company} year {year}')
            return all_urls
        except Exception as e:
            logger.error(f'Error searching ESG reports for {company}: {e}')
            return []
    def search_esg_reports_api(self, company: str, website: str, years: str='2024', max_results: int=5) -> List[Dict[str, str]]:
        """
        Search for ESG reports using Google Custom Search API with year-based queries.
        Args:
            company (str): Company name
            website (str): Company website
            years (str): Comma-separated years (e.g., "2023,2024")
            max_results (int): Maximum number of results to return per year
        Returns:
            List[Dict[str, str]]: List of dictionaries with URL and year
        """
        try:
            years_list = years.split(',') if years else ['2024']
            all_urls = []
            for year in years_list:
                year = year.strip()
                cache_key = f'esg_urls_api:{company}:{website}:{year}'
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    logger.info(f'API cache hit for {company} year {year}')
                    cached_urls = json.loads(cached_result)
                    all_urls.extend([{'url': url, 'year': year} for url in cached_urls])
                    continue
                query = f'site:{website} (ESG report OR sustainability report) {year} filetype:pdf'
                result = self.service.cse().list(q=query, cx=self.cse_id, num=max_results).execute()
                year_urls = []
                for item in result.get('items', []):
                    url = item.get('link')
                    if url and self._is_valid_pdf_url(url):
                        year_urls.append(url)
                self.redis_client.setex(cache_key, 86400, json.dumps(year_urls))
                for url in year_urls:
                    all_urls.append({'url': url, 'year': year})
                logger.info(f'Found {len(year_urls)} valid ESG URLs for {company} year {year} via API')
            return all_urls
        except Exception as e:
            logger.error(f'Error searching ESG reports for {company} via API: {e}')
            return []
    def _is_valid_pdf_url(self, url: str) -> bool:
        """
        Check if URL is a valid PDF link.
        Args:
            url (str): URL to validate
        Returns:
            bool: True if valid PDF URL
        """
        try:
            parsed = urlparse(url)
            if url.lower().endswith('.pdf') or 'pdf' in url.lower():
                return True
            response = requests.head(url, timeout=5)
            content_type = response.headers.get('content-type', '').lower()
            return 'pdf' in content_type
        except Exception:
            return False
    def load_companies_from_csv(self, csv_path: str) -> List[Dict[str, str]]:
        """
        Load companies from CSV file.
        Args:
            csv_path (str): Path to CSV file
        Returns:
            List[Dict]: List of company dictionaries
        """
        try:
            df = pd.read_csv(csv_path)
            companies = df.to_dict('records')
            logger.info(f'Loaded {len(companies)} companies from CSV')
            return companies
        except Exception as e:
            logger.error(f'Error loading companies from CSV: {e}')
            return []
    def save_urls_to_db(self, company: str, ticker: str, urls: List[Dict[str, str]]):
        """
        Save URLs with year information to database.
        Args:
            company (str): Company name
            ticker (str): Stock ticker
            urls (List[Dict[str, str]]): List of URL dictionaries with year
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS esg_urls (\n                    id SERIAL PRIMARY KEY,\n                    company VARCHAR(255),\n                    ticker VARCHAR(50),\n                    url TEXT,\n                    year INTEGER,\n                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                )\n            ')
            cursor.execute('\n                ALTER TABLE esg_urls ADD COLUMN IF NOT EXISTS year INTEGER\n            ')
            for url_info in urls:
                cursor.execute('\n                    INSERT INTO esg_urls (company, ticker, url, year) \n                    VALUES (%s, %s, %s, %s)\n                    ON CONFLICT DO NOTHING\n                ', (company, ticker, url_info['url'], int(url_info['year'])))
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f'Saved {len(urls)} URLs with year info for {company} to database')
        except Exception as e:
            logger.error(f'Error saving URLs to database: {e}')
    def scrape_all_companies(self, csv_path: str, max_companies: Optional[int]=None) -> pd.DataFrame:
        """
        Scrape ESG URLs for all companies in CSV file with year support.
        Args:
            csv_path (str): Path to companies CSV file
            max_companies (Optional[int]): Maximum number of companies to process
        Returns:
            pd.DataFrame: DataFrame with results
        """
        companies = self.load_companies_from_csv(csv_path)
        if max_companies:
            companies = companies[:max_companies]
        results = []
        for i, company_data in enumerate(companies, 1):
            company = company_data['company']
            ticker = company_data['ticker']
            website = company_data['website']
            years = company_data.get('report_years', '2024')
            logger.info(f'Processing {i}/{len(companies)}: {company} for years {years}')
            if self.use_custom_search:
                urls = self.search_esg_reports_api(company, website, years)
            else:
                urls = self.search_esg_reports_free(company, website, years)
            if urls:
                self.save_urls_to_db(company, ticker, urls)
            results.append({'company': company, 'ticker': ticker, 'website': website, 'report_years': years, 'urls_found': len(urls), 'urls': urls})
            time.sleep(1)
        df = pd.DataFrame(results)
        output_path = 'data/esg_urls_with_years.csv'
        df.to_csv(output_path, index=False)
        logger.info(f'Scraping complete. Results saved to {output_path}')
        return df
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
