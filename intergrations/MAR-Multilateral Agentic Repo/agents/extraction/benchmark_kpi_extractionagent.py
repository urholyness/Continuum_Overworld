
class benchmark_kpi_extractionAgent:
    """Agent based on benchmark_kpi_extraction from ..\Archieves\Stat-R_AI\esg_kpi_mvp\tests\end_to_end_benchmark.py"""
    
    def __init__(self):
        self.name = "benchmark_kpi_extractionAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Benchmark KPI extraction with real PDF"""
    print('\n🔬 Benchmarking KPI Extraction Performance')
    print('-' * 50)
    test_url = 'https://www.apple.com/environment/pdf/Apple_Environmental_Progress_Report_2023.pdf'
    extractor = ESGKPIExtractor()
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    print(f'Processing: Apple ESG Report')
    result = extractor.process_pdf_url('Apple Inc.', 'AAPL', test_url)
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
    processing_time = end_time - start_time
    memory_used = end_memory - start_memory
    kpi_metrics = {'success': result.success, 'kpis_extracted': len(result.kpis_extracted), 'processing_time': processing_time, 'text_length': result.text_length, 'document_pages': result.document_pages, 'memory_used_mb': memory_used, 'peak_memory_mb': end_memory, 'kpis_per_second': len(result.kpis_extracted) / processing_time if processing_time > 0 else 0, 'characters_per_second': result.text_length / processing_time if processing_time > 0 else 0}
    print(f'\n📊 KPI Extraction Metrics:')
    print(f"  Success: {kpi_metrics['success']}")
    print(f"  KPIs Extracted: {kpi_metrics['kpis_extracted']}")
    print(f"  Processing Time: {kpi_metrics['processing_time']:.2f}s")
    print(f"  Text Length: {kpi_metrics['text_length']:,} characters")
    print(f"  Memory Used: {kpi_metrics['memory_used_mb']:.1f}MB")
    print(f"  KPIs per Second: {kpi_metrics['kpis_per_second']:.2f}")
    print(f"  Characters per Second: {kpi_metrics['characters_per_second']:,.0f}")
    kpi_categories = {}
    for kpi in result.kpis_extracted:
        category = kpi.kpi_name.split('_')[0]
        kpi_categories[category] = kpi_categories.get(category, 0) + 1
    print(f'\n📋 KPI Categories Found:')
    for category, count in sorted(kpi_categories.items()):
        print(f'  {category}: {count} KPIs')
    return (result, kpi_metrics)
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
