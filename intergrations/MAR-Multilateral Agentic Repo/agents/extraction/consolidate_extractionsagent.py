
class consolidate_extractionsAgent:
    """Agent based on consolidate_extractions from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_ai_extraction_chunked.py"""
    
    def __init__(self):
        self.name = "consolidate_extractionsAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Combine results from multiple chunks and resolve duplicates"""
    all_extractions = []
    for chunk_result in chunk_results:
        if chunk_result['success']:
            all_extractions.extend(chunk_result.get('extractions', []))
    kpi_groups = {}
    for extraction in all_extractions:
        kpi_name = extraction.get('kpi_name', 'unknown')
        if kpi_name not in kpi_groups:
            kpi_groups[kpi_name] = []
        kpi_groups[kpi_name].append(extraction)
    consolidated = []
    for kpi_name, extractions in kpi_groups.items():
        if extractions:
            best = max(extractions, key=lambda x: x.get('confidence', 0))
            consolidated.append(best)
    return consolidated
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
