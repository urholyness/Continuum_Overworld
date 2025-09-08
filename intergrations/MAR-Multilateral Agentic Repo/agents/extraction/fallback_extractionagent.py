
class fallback_extractionAgent:
    """Agent based on fallback_extraction from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_document_ai.py"""
    
    def __init__(self):
        self.name = "fallback_extractionAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Fallback regex extraction for missed KPIs"""
    kpis = []
    for page_idx, page_text in enumerate(text_pages):
        page_num = start_page + page_idx + 1
        for kpi_name, patterns in self.fallback_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    try:
                        value_str = match.group(1).replace(',', '')
                        kpi_value = float(value_str)
                        kpi_unit = match.group(2) if len(match.groups()) > 1 else self.get_default_unit(kpi_name)
                        start_pos = max(0, match.start() - 100)
                        end_pos = min(len(page_text), match.end() + 100)
                        context_text = page_text[start_pos:end_pos]
                        kpi = KPIMetadata(company=company, ticker=ticker, kpi_name=kpi_name, kpi_value=kpi_value, kpi_unit=kpi_unit, kpi_year=year, confidence_score=0.75, source_url='', extraction_method='regex_fallback', report_name='', page_number=page_num, matched_text=match.group(0), context_text=context_text, created_at=datetime.now())
                        kpis.append(kpi)
                    except (ValueError, IndexError):
                        continue
    return kpis
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
