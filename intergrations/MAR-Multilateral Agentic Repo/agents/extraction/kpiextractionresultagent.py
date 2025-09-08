
class KPIExtractionResultAgent:
    """Agent based on KPIExtractionResult from ..\Rank_AI\04_kpi_extraction\ai_kpi_extractor.py"""
    
    def __init__(self):
        self.name = "KPIExtractionResultAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
        class KPIExtractionResult:
    """Results from KPI extraction process"""
    kpi_key: str
    kpi_name: str
    value: Optional[float]
    unit: Optional[str]
    confidence: float
    source: str
    extraction_method: str
    patterns_matched: List[str]
    context_snippet: Optional[str] = None
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
