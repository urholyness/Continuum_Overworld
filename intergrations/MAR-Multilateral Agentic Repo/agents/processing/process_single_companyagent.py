
class process_single_companyAgent:
    """Agent based on process_single_company from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\batch_testing_50_companies.py"""
    
    def __init__(self):
        self.name = "process_single_companyAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Process a single company's ESG report with year support"""
    start_time = time.time()
    result = {'company': company, 'pdf_url': pdf_url, 'year': year, 'success': False, 'kpis_extracted': 0, 'greenwashing_score': 0.0, 'flagged_sections': 0, 'processing_time': 0.0, 'error': None, 'metadata': {}}
    try:
        print(f'🔄 Processing {company} for year {year}...')
        ticker = ''.join([c for c in company.upper() if c.isalpha()])[:4]
        kpis, greenwashing = self.extractor.process_pdf_with_metadata(pdf_url, company, ticker, year)
        result['success'] = True
        result['kpis_extracted'] = len(kpis)
        result['processing_time'] = time.time() - start_time
        if greenwashing:
            result['greenwashing_score'] = greenwashing.overall_score
            result['flagged_sections'] = len(greenwashing.flagged_sections)
            result['metadata']['indicator_scores'] = greenwashing.indicator_scores
            result['metadata']['report_name'] = greenwashing.report_name
            result['metadata']['analysis_year'] = greenwashing.analysis_year
        if kpis:
            result['metadata']['sample_kpis'] = [{'name': kpi.kpi_name, 'value': kpi.kpi_value, 'unit': kpi.kpi_unit, 'year': kpi.kpi_year, 'page': kpi.page_number, 'confidence': kpi.confidence_score} for kpi in kpis[:5]]
            avg_confidence = sum((kpi.confidence_score for kpi in kpis)) / len(kpis)
            result['metadata']['avg_confidence'] = avg_confidence
            env_kpis = len([k for k in kpis if 'carbon' in k.kpi_name.lower() or 'energy' in k.kpi_name.lower() or 'water' in k.kpi_name.lower()])
            social_kpis = len([k for k in kpis if 'diversity' in k.kpi_name.lower() or 'safety' in k.kpi_name.lower()])
            governance_kpis = len([k for k in kpis if 'board' in k.kpi_name.lower() or 'ethics' in k.kpi_name.lower()])
            result['metadata']['kpi_categories'] = {'environmental': env_kpis, 'social': social_kpis, 'governance': governance_kpis}
        self.extractor.save_results_to_database(kpis, greenwashing)
        print(f"✅ {company} ({year}): {len(kpis)} KPIs, GW Score: {result['greenwashing_score']:.1f}")
    except Exception as e:
        result['error'] = str(e)
        result['processing_time'] = time.time() - start_time
        print(f'❌ {company} ({year}): Error - {str(e)[:100]}...')
    return result
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
