
class process_csv_fileAgent:
    """Agent based on process_csv_file from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_csv_processor.py"""
    
    def __init__(self):
        self.name = "process_csv_fileAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Process CSV file and extract KPIs from companies"""
    print(f'🔄 Processing CSV file: {csv_path}')
    from kpi_extractor import ESGKPIExtractor
    companies_df = pd.read_csv(csv_path)
    print(f'📋 Found {len(companies_df)} companies to process')
    extractor = ESGKPIExtractor()
    print('✅ KPI extractor initialized')
    results = []
    for index, row in companies_df.iterrows():
        company = row['company']
        ticker = row['ticker']
        website = row['website']
        print(f'🔄 Processing {company} ({ticker})...')
        test_urls = []
        if 'apple' in company.lower():
            test_urls.append('https://www.apple.com/environment/pdf/Apple_Environmental_Progress_Report_2023.pdf')
        elif 'adobe' in company.lower():
            test_urls.append('https://www.adobe.com/content/dam/cc/en/corporate-responsibility/pdfs/Adobe-CSR-Report-2023.pdf')
        elif 'exxon' in company.lower():
            test_urls.append('https://corporate.exxonmobil.com/-/media/global/files/sustainability-report/2024/sustainability-report.pdf')
        else:
            test_urls = [f'{website}/sustainability-report.pdf', f'{website}/esg-report.pdf', f'{website}/environmental-report.pdf']
        success = False
        for url in test_urls:
            try:
                print(f'  🔄 Trying: {url}')
                result = extractor.process_pdf_url(company, ticker, url)
                if result.success:
                    print(f'  ✅ Success! Extracted {len(result.kpis_extracted)} KPIs')
                    results.append({'company': company, 'ticker': ticker, 'url': url, 'kpis_count': len(result.kpis_extracted), 'processing_time': result.processing_time, 'success': True})
                    success = True
                    break
                else:
                    print(f'  ❌ Failed: {result.error_message}')
            except Exception as e:
                print(f'  ❌ Error: {e}')
                continue
        if not success:
            print(f'  ⚠️ No ESG reports found for {company}')
            results.append({'company': company, 'ticker': ticker, 'url': None, 'kpis_count': 0, 'processing_time': 0, 'success': False})
    successful = sum((1 for r in results if r['success']))
    total_kpis = sum((r['kpis_count'] for r in results))
    print(f'\n🎯 Processing Summary:')
    print(f'  Companies processed: {len(results)}')
    print(f'  Successful extractions: {successful}')
    print(f'  Total KPIs extracted: {total_kpis}')
    return results
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
