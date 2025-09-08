
class _extract_numeric_from_rowAgent:
    """Agent based on _extract_numeric_from_row from ..\Rank_AI\04_kpi_extraction\ai_kpi_extractor.py"""
    
    def __init__(self):
        self.name = "_extract_numeric_from_rowAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract numeric value from table row"""
    for col_idx in range(start_col + 1, len(row)):
        value = self._parse_numeric_value(str(row[col_idx]))
        if value is not None:
            return value
    for col_idx in range(start_col - 1, -1, -1):
        value = self._parse_numeric_value(str(row[col_idx]))
        if value is not None:
            return value
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
