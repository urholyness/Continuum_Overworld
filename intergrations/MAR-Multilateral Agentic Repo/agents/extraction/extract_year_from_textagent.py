
class extract_year_from_textAgent:
    """Agent based on extract_year_from_text from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_enhanced.py"""
    
    def __init__(self):
        self.name = "extract_year_from_textAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract year from text context"""
    year_patterns = ['20[12]\\d', '\\b(20[12]\\d)\\b']
    for pattern in year_patterns:
        matches = re.findall(pattern, text)
        if matches:
            return int(matches[-1])
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
