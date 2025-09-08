
class _extract_from_tablesAgent:
    """Agent based on _extract_from_tables from ..\Rank_AI\04_kpi_extraction\ai_kpi_extractor.py"""
    
    def __init__(self):
        self.name = "_extract_from_tablesAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract KPIs from structured table data"""
    results = {}
    if not tables:
        return results
    for table in tables:
        table_data = table.get('data', [])
        table_id = table.get('table_id', 'unknown')
        if not table_data:
            continue
        for kpi_key, kpi_config in target_kpis.items():
            if kpi_key in results:
                continue
            patterns = kpi_config.get('patterns', [])
            units = kpi_config.get('units', [])
            for row_idx, row in enumerate(table_data):
                for col_idx, cell in enumerate(row):
                    cell_str = str(cell).lower()
                    matched_patterns = [p for p in patterns if p.lower() in cell_str]
                    if matched_patterns:
                        value = self._extract_numeric_from_row(row, col_idx, units)
                        if value is not None:
                            results[kpi_key] = KPIExtractionResult(kpi_key=kpi_key, kpi_name=kpi_config['name'], value=value, unit=self._detect_unit(row, units), confidence=0.95, source=f'table_{table_id}', extraction_method='table_analysis', patterns_matched=matched_patterns, context_snippet=f"Row {row_idx}: {' | '.join(map(str, row))}")
                            break
    return results
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
