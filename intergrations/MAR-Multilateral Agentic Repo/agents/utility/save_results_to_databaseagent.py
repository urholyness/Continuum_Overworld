
class save_results_to_databaseAgent:
    """Agent based on save_results_to_database from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\esg_scraper_patched.py"""
    
    def __init__(self):
        self.name = "save_results_to_databaseAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
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
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
