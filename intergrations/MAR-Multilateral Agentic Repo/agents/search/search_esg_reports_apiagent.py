
class search_esg_reports_apiAgent:
    """Agent based on search_esg_reports_api from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\scrape_esg_urls.py"""
    
    def __init__(self):
        self.name = "search_esg_reports_apiAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
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
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
