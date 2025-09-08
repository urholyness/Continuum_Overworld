
class extract_kpisAgent:
    """Agent based on extract_kpis from ..\Rank_AI\04_kpi_extraction\ai_kpi_extractor.py"""
    
    def __init__(self):
        self.name = "extract_kpisAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """
        Main KPI extraction method with configurable parameters
        Args:
            content: Raw document content from Stage 3
            company_name: Company name for context
            reporting_year: Reporting year for validation
            target_kpis: Specific KPIs to extract (None = use default set)
            structured_tables: Table data from Stage 3
            processing_mode: "comprehensive", "targeted", "high_confidence"
        Returns:
            ESGExtractionState with extraction results
        """
    if target_kpis:
        kpis_to_extract = {k: v for k, v in self.target_kpis.items() if k in target_kpis}
        state.agent_logs.append({'agent': 'KPISelector', 'action': 'filter_target_kpis', 'status': 'success', 'details': f'Filtering to {len(kpis_to_extract)} specific KPIs: {target_kpis}', 'timestamp': datetime.now().isoformat()})
    else:
        kpis_to_extract = self.target_kpis
    state.target_kpis = kpis_to_extract
    extraction_results = {}
    table_results = self._extract_from_tables(structured_tables, kpis_to_extract) if structured_tables else {}
    content_results = self._extract_from_content(content, kpis_to_extract)
    for kpi_key, kpi_config in kpis_to_extract.items():
        table_result = table_results.get(kpi_key)
        content_result = content_results.get(kpi_key)
        if table_result and table_result.confidence >= state.confidence_threshold:
            extraction_results[kpi_key] = table_result
        elif content_result and content_result.confidence >= state.confidence_threshold:
            extraction_results[kpi_key] = content_result
        elif processing_mode != 'high_confidence':
            best_result = max([r for r in [table_result, content_result] if r], key=lambda x: x.confidence, default=None)
            if best_result:
                extraction_results[kpi_key] = best_result
    state.extracted_kpis = extraction_results
    found_kpis = len([r for r in extraction_results.values() if r.value is not None])
    total_kpis = len(kpis_to_extract)
    state.extraction_metadata = {'extraction_rate': f'{found_kpis}/{total_kpis} ({found_kpis / total_kpis * 100:.1f}%)', 'processing_mode': processing_mode, 'confidence_threshold': state.confidence_threshold, 'extraction_methods': ['table_analysis', 'content_pattern_matching'], 'performance_metrics': {'found_kpis': found_kpis, 'total_targets': total_kpis, 'success_rate': found_kpis / total_kpis if total_kpis > 0 else 0}}
    state.agent_logs.append({'agent': 'AIKPIExtractor', 'action': 'extract_kpis_complete', 'status': 'success', 'details': f'Extracted {found_kpis}/{total_kpis} KPIs ({found_kpis / total_kpis * 100:.1f}%)', 'timestamp': datetime.now().isoformat()})
    state.coordination_metadata['extraction_end'] = datetime.now().isoformat()
    return state
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
