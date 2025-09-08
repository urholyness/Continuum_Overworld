
class extract_kpis_regexAgent:
    """Agent based on extract_kpis_regex from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor.py"""
    
    def __init__(self):
        self.name = "extract_kpis_regexAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """
        Extract KPIs using regex patterns
        Args:
            text (str): Extracted text from PDF
        Returns:
            List[KPIData]: List of extracted KPIs
        """
    kpis = []
    text_clean = re.sub('\\s+', ' ', text.lower())
    year_match = re.search('20(1[0-9]|2[0-9])', text)
    document_year = int(year_match.group()) if year_match else None
    for kpi_name, config in self.kpi_patterns.items():
        for pattern in config['patterns']:
            matches = re.finditer(pattern, text_clean, re.IGNORECASE)
            for match in matches:
                try:
                    value_str = match.group(1).replace(',', '')
                    value = float(value_str)
                    unit = config['unit']
                    if len(match.groups()) > 1 and match.group(2):
                        unit = match.group(2)
                    kpi = KPIData(company='', ticker='', kpi_name=kpi_name, kpi_value=value, kpi_unit=unit, kpi_year=document_year, confidence_score=0.7, source_url='', extraction_method='regex', raw_text=match.group(0))
                    kpis.append(kpi)
                except (ValueError, IndexError) as e:
                    logger.debug(f'Error parsing KPI match: {e}')
                    continue
    return kpis
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
