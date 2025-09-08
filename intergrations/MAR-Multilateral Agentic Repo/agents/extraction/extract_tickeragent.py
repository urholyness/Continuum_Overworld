
class extract_tickerAgent:
    """Agent based on extract_ticker from ..\Archieves\Stat-R_AI\esg_kpi_mvp\tests\test_enhanced_survey_basic.py"""
    
    def __init__(self):
        self.name = "extract_tickerAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
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
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
