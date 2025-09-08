
class ExtractionResultAgent:
    """Agent based on ExtractionResult from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor.py"""
    
    def __init__(self):
        self.name = "ExtractionResultAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
        class ExtractionResult:
    """Data class for extraction results"""
    company: str
    ticker: str
    source_url: str
    kpis_extracted: List[KPIData]
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    document_pages: int = 0
    text_length: int = 0
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
