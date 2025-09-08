
class test_ticker_extractionAgent:
    """Agent based on test_ticker_extraction from ..\Archieves\Stat-R_AI\esg_kpi_mvp\tests\test_enhanced_survey_basic.py"""
    
    def __init__(self):
        self.name = "test_ticker_extractionAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Test ticker symbol extraction without importing full system"""
    print('🧪 Testing Ticker Extraction...')
    def extract_ticker(company: str) -> str:
        """Extract or generate ticker symbol from company name"""
        if 'Inc.' in company:
            ticker = company.replace(' Inc.', '').replace(' ', '')[:4].upper()
        elif 'Corp' in company:
            ticker = company.replace(' Corp', '').replace(' ', '')[:4].upper()
        elif 'Corporation' in company:
            ticker = company.replace(' Corporation', '').replace(' ', '')[:4].upper()
        else:
            ticker = company.replace(' ', '')[:4].upper()
        return ticker
    test_cases = [('Apple Inc.', 'APPL'), ('Microsoft Corp', 'MICR'), ('Tesla Corporation', 'TESL'), ('Amazon', 'AMAZ')]
    for company, expected_prefix in test_cases:
        ticker = extract_ticker(company)
        if ticker.startswith(expected_prefix[:3]) and ticker.isupper() and (len(ticker) <= 4):
            print(f'  ✅ {company} -> {ticker}')
        else:
            print(f'  ❌ {company} -> {ticker} (expected {expected_prefix})')
    print(f'✅ Ticker extraction: {success_rate:.0f}% success rate')
    return success_rate
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
