
class test_api_search_failureAgent:
    """Agent based on test_api_search_failure from ..\Archieves\Stat-R_AI\esg_kpi_mvp\tests\test_esg_scraper.py"""
    
    def __init__(self):
        self.name = "test_api_search_failureAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
        def test_api_search_failure(self, mock_build):
    """Test API search failure handling"""
    from googleapiclient.errors import HttpError
    mock_service = Mock()
    mock_cse = Mock()
    mock_list = Mock()
    mock_list.execute.side_effect = HttpError(resp=Mock(status=403), content=b'{"error": {"code": 403, "message": "Daily Limit Exceeded"}}')
    mock_cse.list.return_value = mock_list
    mock_service.cse.return_value = mock_cse
    mock_build.return_value = mock_service
    scraper = ESGURLScraperV2(api_key='test_key', cse_id='test_cse')
    scraper.redis_client = self.mock_redis
    self.mock_redis.get.return_value = None
    result = scraper.search_esg_reports_api('Test Corp', 'testcorp.com')
    self.assertFalse(result.success)
    self.assertEqual(len(result.urls), 0)
    self.assertIsNotNone(result.error_message)
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
