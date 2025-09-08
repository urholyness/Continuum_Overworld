
class process_document_ai_entityAgent:
    """Agent based on process_document_ai_entity from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_document_ai.py"""
    
    def __init__(self):
        self.name = "process_document_ai_entityAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Process a Document AI entity into KPI metadata"""
    try:
        entity_type = entity.type_
        kpi_name = self.kpi_entity_mapping.get(entity_type)
        if not kpi_name:
        mention_text = entity.mention_text
        confidence = entity.confidence
        value_match = re.search('(\\d+[\\d,]*(?:\\.\\d+)?)', mention_text)
        if not value_match:
        kpi_value = float(value_match.group(1).replace(',', ''))
        unit_match = re.search('(mt|tonnes?|tons?|tco2e?|%|kwh|mwh|gwh)', mention_text.lower())
        kpi_unit = unit_match.group(1) if unit_match else self.get_default_unit(kpi_name)
        context_start = max(0, page_text.find(mention_text) - 100)
        context_end = min(len(page_text), page_text.find(mention_text) + len(mention_text) + 100)
        context_text = page_text[context_start:context_end]
        return KPIMetadata(company=company, ticker=ticker, kpi_name=kpi_name, kpi_value=kpi_value, kpi_unit=kpi_unit, kpi_year=year, confidence_score=confidence, source_url='', extraction_method='document_ai', report_name='', page_number=page_num, matched_text=mention_text, context_text=context_text, created_at=datetime.now())
    except Exception as e:
        logger.warning(f'Failed to process entity: {e}')
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
