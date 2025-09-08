
class search_esg_reports_freeAgent:
    """Agent based on search_esg_reports_free from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\scrape_esg_urls.py"""
    
    def __init__(self):
        self.name = "search_esg_reports_freeAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
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
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
