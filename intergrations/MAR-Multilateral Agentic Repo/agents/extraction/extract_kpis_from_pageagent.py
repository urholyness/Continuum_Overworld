
class extract_kpis_from_pageAgent:
    """Agent based on extract_kpis_from_page from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_enhanced.py"""
    
    def __init__(self):
        self.name = "extract_kpis_from_pageAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract KPIs from a single page with metadata and year tagging"""
    kpis = []
    for kpi_name, config in self.kpi_patterns.items():
        for pattern in config['patterns']:
            try:
                for match in re.finditer(pattern, page_text, re.IGNORECASE):
                    value_str = match.group(1).replace(',', '')
                    try:
                        kpi_value = float(value_str)
                    except ValueError:
                        continue
                    context_text = self.get_context_text(page_text, match.start(), match.end())
                    kpi_year = input_year or self.extract_year_from_text(context_text)
                    if not kpi_year:
                        kpi_year = 2024
                    confidence_score = self.calculate_confidence_score(match.group(0), context_text, config.get('context_words', []))
                    kpi = KPIMetadata(company=company, ticker=ticker, kpi_name=kpi_name, kpi_value=kpi_value, kpi_unit=config['unit'], kpi_year=kpi_year, confidence_score=confidence_score, source_url=source_url, extraction_method='regex_enhanced', report_name=report_name, page_number=page_number, matched_text=match.group(0), context_text=context_text, created_at=datetime.now())
                    kpis.append(kpi)
            except Exception as e:
                logger.warning(f'Error processing pattern {pattern} for {kpi_name}: {e}')
                continue
    return kpis
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
