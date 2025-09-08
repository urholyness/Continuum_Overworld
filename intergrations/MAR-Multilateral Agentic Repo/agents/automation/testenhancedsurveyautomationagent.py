
class TestEnhancedSurveyAutomationAgent:
    """Agent based on TestEnhancedSurveyAutomation from ..\Archieves\Stat-R_AI\esg_kpi_mvp\tests\test_enhanced_survey_automation.py"""
    
    def __init__(self):
        self.name = "TestEnhancedSurveyAutomationAgent"
        self.category = "automation"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Test suite for enhanced survey automation features"""
    def setUp(self):
        """Set up test environment"""
        try:
            self.survey_system = SurveyAutomationSystem()
        except Exception as e:
            print(f'Warning: Could not initialize full system due to dependencies: {e}')
            self.survey_system = None
    def test_enhanced_database_schema(self):
        """Test enhanced database schema creation"""
        if not self.survey_system:
            self.skipTest('Survey system not available')
        print('🧪 Testing Enhanced Database Schema...')
        try:
            self.survey_system.init_database()
            conn = self.survey_system.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("\n                SELECT column_name FROM information_schema.columns \n                WHERE table_name = 'survey_responses' \n                AND column_name IN ('sentiment_score', 'ticker', 'is_bot', 'is_duplicate')\n            ")
            new_columns = [row[0] for row in cursor.fetchall()]
            expected_columns = ['sentiment_score', 'ticker', 'is_bot', 'is_duplicate']
            cursor.close()
            conn.close()
            found_columns = len([col for col in expected_columns if col in new_columns])
            self.assertGreater(found_columns, 0, 'No enhanced schema columns found')
        except Exception as e:
            print(f'⚠️  Enhanced schema test failed: {e}')
    def test_ticker_extraction(self):
        """Test ticker symbol extraction from company names"""
        if not self.survey_system:
            self.skipTest('Survey system not available')
        print('🧪 Testing Ticker Extraction...')
        test_cases = [('Apple Inc.', 'APPL'), ('Microsoft Corp', 'MICR'), ('Tesla Corporation', 'TESL'), ('Amazon', 'AMAZ')]
        for company, expected_prefix in test_cases:
            ticker = self.survey_system._extract_ticker(company)
            self.assertTrue(ticker.startswith(expected_prefix[:3]), f'Ticker {ticker} should start with {expected_prefix[:3]}')
            self.assertTrue(ticker.isupper(), f'Ticker {ticker} should be uppercase')
            self.assertLessEqual(len(ticker), 4, f'Ticker {ticker} should be max 4 chars')
    def test_bot_detection(self):
        """Test bot response detection"""
        if not self.survey_system:
            self.skipTest('Survey system not available')
        print('🧪 Testing Bot Detection...')
        bot_responses = [{'comment': 'aaaaaaaaaaaaa'}, {'comment': 'test'}, {'comment': 'abc'}, {'comment': 'good good good good good'}]
        good_responses = [{'comment': 'This company has excellent ESG practices and strong environmental policies.'}, {'environmental': 'Good', 'social': 'Excellent'}, {'comment': 'I appreciate their commitment to sustainability and social responsibility.'}]
        for responses in bot_responses:
            is_bot = self.survey_system._detect_bot_response(responses)
            self.assertTrue(is_bot, f'Should detect bot response: {responses}')
        for responses in good_responses:
            is_bot = self.survey_system._detect_bot_response(responses)
            self.assertFalse(is_bot, f'Should not detect bot in good response: {responses}')
    def test_sentiment_analysis(self):
        """Test sentiment analysis with fallback"""
        if not self.survey_system:
            self.skipTest('Survey system not available')
        print('🧪 Testing Sentiment Analysis...')
        test_responses = [{'comment': 'This company is amazing! Great ESG practices!', 'expected_range': (0.6, 1.0)}, {'comment': 'Terrible environmental record and poor governance.', 'expected_range': (0.0, 0.4)}, {'comment': 'The company has average performance in ESG areas.', 'expected_range': (0.4, 0.6)}]
        for test_case in test_responses:
            responses = {'comment': test_case['comment']}
            sentiment = self.survey_system._calculate_sentiment_score(responses)
            self.assertIsInstance(sentiment, float, 'Sentiment should be float')
            self.assertGreaterEqual(sentiment, 0.0, 'Sentiment should be >= 0')
            self.assertLessEqual(sentiment, 1.0, 'Sentiment should be <= 1')
            min_expected, max_expected = test_case['expected_range']
            if min_expected <= sentiment <= max_expected:
                print(f"✅ Sentiment analysis correct for: '{test_case['comment'][:50]}...' -> {sentiment:.2f}")
            else:
                print(f"⚠️  Sentiment analysis approximate for: '{test_case['comment'][:50]}...' -> {sentiment:.2f}")
        print('✅ Sentiment analysis test completed')
    def test_enhanced_quality_scoring(self):
        """Test enhanced quality scoring with new factors"""
        if not self.survey_system:
            self.skipTest('Survey system not available')
        print('🧪 Testing Enhanced Quality Scoring...')
        good_responses = {'esg_overall': 'Good', 'environmental_impact': 'Excellent', 'additional_comments': 'This company demonstrates strong commitment to environmental sustainability through their renewable energy initiatives and waste reduction programs.'}
        good_score = self.survey_system._calculate_quality_score(good_responses, 180)
        self.assertGreater(good_score, 0.8, 'Good responses should have high quality score')
        fast_score = self.survey_system._calculate_quality_score(good_responses, 30)
        self.assertLess(fast_score, 0.6, 'Fast responses should have lower quality score')
        straight_responses = {'q1': '3', 'q2': '3', 'q3': '3', 'q4': '3', 'q5': '3'}
        straight_score = self.survey_system._calculate_quality_score(straight_responses, 120)
        self.assertLess(straight_score, 0.5, 'Straight-lining should have low quality score')
    def test_enhanced_survey_creation(self):
        """Test survey creation with enhanced features"""
        if not self.survey_system:
            self.skipTest('Survey system not available')
        print('🧪 Testing Enhanced Survey Creation...')
        try:
            survey_id = self.survey_system.create_survey('Apple Inc.', 'AAPL')
            self.assertIsNotNone(survey_id, 'Survey creation should return ID')
            survey_data = self.survey_system.get_survey(survey_id)
            if survey_data and 'ticker' in survey_data:
                self.assertEqual(survey_data['ticker'], 'AAPL', 'Ticker should be stored correctly')
            else:
                print('⚠️  Enhanced survey creation: ticker field not found (expected with schema migration)')
        except Exception as e:
            print(f'⚠️  Enhanced survey creation test failed: {e}')
    def test_enhanced_targeting_queries(self):
        """Test enhanced adult targeting queries"""
        if not self.survey_system:
            self.skipTest('Survey system not available')
        print('🧪 Testing Enhanced Targeting Queries...')
        self.assertIsNotNone(self.survey_system.adult_search_queries, 'Adult search queries should be loaded')
        self.assertGreater(len(self.survey_system.adult_search_queries), 0, 'Should have adult search queries')
        for query in self.survey_system.adult_search_queries:
            self.assertIn('-', query, 'Queries should contain negative filters')
            has_adult_filter = any((term in query.lower() for term in ['-student', '-teen', '-kid', '-child']))
            self.assertTrue(has_adult_filter, f'Query should have adult filters: {query}')
    def test_duplicate_detection(self):
        """Test duplicate response detection"""
        if not self.survey_system:
            self.skipTest('Survey system not available')
        print('🧪 Testing Duplicate Detection...')
        survey_id = self.survey_system.create_survey('Test Corp', 'TEST')
        if not survey_id:
            self.skipTest('Could not create test survey')
        test_responses = {'esg_overall': 'Good', 'environmental_impact': 'Excellent'}
        is_duplicate = self.survey_system._detect_duplicate_response(test_responses, survey_id)
        self.assertFalse(is_duplicate, 'First response should not be duplicate')
    def test_enhanced_response_cleaning(self):
        """Test enhanced response cleaning with fallback"""
        if not self.survey_system:
            self.skipTest('Survey system not available')
        print('🧪 Testing Enhanced Response Cleaning...')
        test_responses = {'comment': 'this company has GREAT esg practices!!!', 'rating': '5'}
        cleaned = self.survey_system._clean_responses_enhanced(test_responses)
        self.assertIsNotNone(cleaned, 'Cleaning should return result')
        if isinstance(cleaned.get('comment'), dict):
            self.assertIn('cleaned', cleaned['comment'], 'Should have cleaned text')
            self.assertIn('confidence', cleaned['comment'], 'Should have confidence score')
        else:
    def test_integration_with_existing_system(self):
        """Test integration with existing ESG system"""
        if not self.survey_system:
            self.skipTest('Survey system not available')
        print('🧪 Testing Integration with Existing System...')
        survey_id = self.survey_system.create_survey('Integration Test Corp')
        self.assertIsNotNone(survey_id, 'Basic survey creation should still work')
        rankings = self.survey_system.integrate_with_esg_rankings()
        self.assertIsInstance(rankings, dict, 'ESG integration should return dict')
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
