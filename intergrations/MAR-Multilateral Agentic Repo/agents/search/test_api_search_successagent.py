
class test_api_search_successAgent:
    """Agent based on test_api_search_success from ..\Archieves\Stat-R_AI\esg_kpi_mvp\tests\test_esg_scraper.py"""
    
    def __init__(self):
        self.name = "test_api_search_successAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
        def test_api_search_success(self, mock_build):
    """Test successful API search"""
    mock_service = Mock()
    mock_cse = Mock()
    mock_list = Mock()
    mock_list.execute.return_value = {'items': [{'link': 'https://testcorp.com/sustainability-report.pdf'}, {'link': 'https://testcorp.com/esg-annual-report.pdf'}]}
    mock_cse.list.return_value = mock_list
    mock_service.cse.return_value = mock_cse
    mock_build.return_value = mock_service
    scraper = ESGURLScraperV2(api_key='test_key', cse_id='test_cse')
    scraper.redis_client = self.mock_redis
    self.mock_redis.get.return_value = None
    result = scraper.search_esg_reports_api('Test Corp', 'testcorp.com')
    self.assertTrue(result.success)
    self.assertEqual(len(result.urls), 2)
    self.assertEqual(result.search_method, 'api')
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
