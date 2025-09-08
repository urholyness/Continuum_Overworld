
class TestESGScraperV2Agent:
    """Agent based on TestESGScraperV2 from ..\Archieves\Stat-R_AI\esg_kpi_mvp\tests\test_esg_scraper.py"""
    
    def __init__(self):
        self.name = "TestESGScraperV2Agent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Comprehensive tests for ESG scraper"""
    def setUp(self):
        """Set up test environment"""
        self.scraper = ESGURLScraperV2()
        self.mock_redis = Mock()
        self.scraper.redis_client = self.mock_redis
        self.test_companies = [{'company': 'Test Corp', 'ticker': 'TEST', 'website': 'testcorp.com'}, {'company': 'Green Inc', 'ticker': 'GREEN', 'website': 'greeninc.com'}]
    def test_pdf_url_validation(self):
        """Test PDF URL validation logic"""
        test_cases = [('https://example.com/report.pdf', True), ('https://example.com/sustainability.PDF', True), ('http://company.com/esg-report.pdf', True)]
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = self.scraper._is_valid_pdf_url(url)
                self.assertEqual(result, expected, f'URL {url} should be {expected}')
    def test_esg_url_detection(self):
        """Test ESG-related URL detection"""
        test_cases = [('https://example.com/sustainability-report.pdf', True), ('https://example.com/esg/annual-report.pdf', True), ('https://example.com/corporate-responsibility.pdf', True), ('https://example.com/financial-report.pdf', False), ('https://example.com/marketing-brochure.pdf', False)]
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = self.scraper._is_esg_related_url(url)
                self.assertEqual(result, expected, f'URL {url} should be {expected}')
    def test_cache_functionality(self):
        """Test Redis caching functionality"""
        cached_data = {'company': 'Test Corp', 'ticker': 'TEST', 'website': 'testcorp.com', 'urls': ['https://testcorp.com/sustainability.pdf'], 'search_method': 'api', 'search_time': 1.5, 'success': True, 'error_message': None}
        self.mock_redis.get.return_value = json.dumps(cached_data)
        result = self.scraper.search_esg_reports_api('Test Corp', 'testcorp.com')
        self.assertEqual(result.company, 'Test Corp')
        self.assertEqual(len(result.urls), 1)
        self.assertTrue(result.success)
        self.mock_redis.get.assert_called_once()
    @patch('requests.get')
    def test_website_scraping(self, mock_get):
        """Test direct website scraping"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '\n        <html>\n            <body>\n                <a href="/sustainability-report.pdf">Sustainability Report 2023</a>\n                <a href="/esg/annual-report.pdf">Annual ESG Report</a>\n                <a href="/financial-report.pdf">Financial Report</a>\n            </body>\n        </html>\n        '
        mock_get.return_value = mock_response
        urls = self.scraper._scrape_company_website('testcorp.com', max_results=5)
        self.assertIsInstance(urls, list)
        esg_urls = [url for url in urls if self.scraper._is_esg_related_url(url)]
        self.assertEqual(len(esg_urls), len(urls))
    @patch('googleapiclient.discovery.build')
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
    @patch('googleapiclient.discovery.build')
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
    @patch('psycopg2.connect')
    def test_database_saving(self, mock_connect):
        """Test database saving functionality"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        test_result = SearchResult(company='Test Corp', ticker='TEST', website='testcorp.com', urls=['https://testcorp.com/sustainability.pdf'], search_method='api', search_time=1.5, success=True)
        self.scraper._save_search_result(test_result)
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    def test_metrics_tracking(self):
        """Test metrics tracking functionality"""
        self.assertEqual(self.scraper.metrics.total_companies, 0)
        self.assertEqual(self.scraper.metrics.successful_searches, 0)
        self.assertEqual(self.scraper.metrics.failed_searches, 0)
        with patch.object(self.scraper, 'search_esg_reports_api') as mock_search:
            mock_search.return_value = SearchResult(company='Test Corp', ticker='TEST', website='testcorp.com', urls=['https://testcorp.com/sustainability.pdf'], search_method='api', search_time=1.5, success=True)
            with patch.object(self.scraper, '_save_search_result'):
                self.scraper.scrape_company('Test Corp', 'TEST', 'testcorp.com')
            self.assertEqual(self.scraper.metrics.successful_searches, 1)
            self.assertEqual(self.scraper.metrics.total_urls_found, 1)
    def test_csv_loading(self):
        """Test CSV loading functionality"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('company,ticker,website\n')
            f.write('Test Corp,TEST,testcorp.com\n')
            f.write('Green Inc,GREEN,greeninc.com\n')
            temp_path = f.name
        try:
            companies = self.scraper.load_companies_from_csv(temp_path)
            self.assertEqual(len(companies), 2)
            self.assertEqual(companies[0]['company'], 'Test Corp')
            self.assertEqual(companies[1]['ticker'], 'GREEN')
        finally:
            os.unlink(temp_path)
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        start_time = time.time()
        with patch.object(self.scraper, 'search_esg_reports_api') as mock_search:
            mock_search.return_value = SearchResult(company='Test Corp', ticker='TEST', website='testcorp.com', urls=[], search_method='api', search_time=0.1, success=True)
            with patch.object(self.scraper, '_save_search_result'):
                for i in range(3):
                    self.scraper.scrape_company(f'Test Corp {i}', 'TEST', 'testcorp.com')
        elapsed = time.time() - start_time
        self.assertGreater(elapsed, 0.1)
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
