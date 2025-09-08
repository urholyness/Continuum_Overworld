
class test_enhanced_extractorAgent:
    """Agent based on test_enhanced_extractor from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_enhanced.py"""
    
    def __init__(self):
        self.name = "test_enhanced_extractorAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Test the enhanced extractor with Apple's ESG report"""
    print('🧪 Testing Enhanced KPI Extractor with Metadata and Greenwashing Analysis')
    print('=' * 80)
    extractor = EnhancedKPIExtractor()
    test_url = 'https://www.apple.com/environment/pdf/Apple_Environmental_Progress_Report_2023.pdf'
    company = 'Apple Inc.'
    ticker = 'AAPL'
    print(f'Testing with: {company}')
    print(f'PDF URL: {test_url}')
    kpis, greenwashing = extractor.process_pdf_with_metadata(test_url, company, ticker)
    print(f'\n📊 EXTRACTION RESULTS')
    print('=' * 40)
    print(f'KPIs Extracted: {len(kpis)}')
    print(f'Greenwashing Score: {greenwashing.overall_score:.1f}')
    if kpis:
        print(f'\n🔍 SAMPLE KPIS (First 5)')
        print('-' * 40)
        for i, kpi in enumerate(kpis[:5]):
            print(f'{i + 1}. {kpi.kpi_name}: {kpi.kpi_value} {kpi.kpi_unit}')
            print(f'   Page: {kpi.page_number}, Confidence: {kpi.confidence_score:.2f}')
            print(f'   Context: {kpi.context_text[:100]}...')
            print()
    if greenwashing:
        print(f'\n🚨 GREENWASHING ANALYSIS')
        print('-' * 40)
        print(f'Overall Score: {greenwashing.overall_score:.1f}')
        print(f'Indicator Scores:')
        for indicator, score in greenwashing.indicator_scores.items():
            print(f'  - {indicator}: {score:.1f}')
        print(f'\nFlagged Sections: {len(greenwashing.flagged_sections)}')
        for flag in greenwashing.flagged_sections[:3]:
            print(f"  - {flag['type']}: {flag['text'][:100]}...")
    extractor.save_results_to_database(kpis, greenwashing)
    print(f'\n✅ Test completed successfully!')
    return (kpis, greenwashing)
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
