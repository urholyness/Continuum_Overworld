
class _save_search_resultAgent:
    """Agent based on _save_search_result from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\esg_scraper_v2.py"""
    
    def __init__(self):
        self.name = "_save_search_resultAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
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
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
