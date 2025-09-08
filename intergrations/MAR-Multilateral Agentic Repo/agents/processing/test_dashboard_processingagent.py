
class test_dashboard_processingAgent:
    """Agent based on test_dashboard_processing from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_dashboard_processing.py"""
    
    def __init__(self):
        self.name = "test_dashboard_processingAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Test the exact same processing that dashboard should do"""
    print('🔄 Testing dashboard processing logic...')
    try:
        from kpi_extractor import ESGKPIExtractor
        print('✅ KPI extractor imported successfully')
    except ImportError as e:
        print(f'❌ Could not import KPI extractor: {e}')
        return False
    csv_path = '/mnt/c/users/georg/documents/projects/Stat-r_AI/esg_kpi_mvp/data/test_companies.csv'
    print(f'📋 Reading CSV: {csv_path}')
    try:
        companies_df = pd.read_csv(csv_path)
        print(f'✅ Found {len(companies_df)} companies in CSV')
    except Exception as e:
        print(f'❌ Error reading CSV: {e}')
        return False
    extractor = ESGKPIExtractor()
    print('✅ Extractor initialized')
    def get_db_connection():
        db_path = '/mnt/c/users/georg/documents/projects/Stat-r_AI/esg_kpi_mvp/esg_kpi.db'
        return sqlite3.connect(db_path)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM extracted_kpis')
    before_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f'📊 KPIs in database before processing: {before_count}')
    print(f'🚀 Starting processing of {len(companies_df)} companies...')
    successful_companies = []
    failed_companies = []
    for index, row in companies_df.iterrows():
        company = row['company']
        ticker = row['ticker']
        esg_url = row.get('esg_report_url', '')
        print(f'\n🔄 Processing {index + 1}/{len(companies_df)}: {company} ({ticker})')
        if esg_url:
            try:
                print(f'  📥 Processing URL: {esg_url}')
                result = extractor.process_pdf_url(company, ticker, esg_url)
                if result.success:
                    print(f'  ✅ Success! Extracted {len(result.kpis_extracted)} KPIs in {result.processing_time:.1f}s')
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM extracted_kpis WHERE company = ? AND ticker = ?', (company, ticker))
                    saved_count = cursor.fetchone()[0]
                    cursor.close()
                    conn.close()
                    print(f'  💾 {saved_count} KPIs saved to database')
                    successful_companies.append({'company': company, 'ticker': ticker, 'kpis_extracted': len(result.kpis_extracted), 'kpis_saved': saved_count, 'processing_time': result.processing_time})
                else:
                    print(f'  ❌ Failed: {result.error_message}')
                    failed_companies.append({'company': company, 'ticker': ticker, 'error': result.error_message})
            except Exception as e:
                print(f'  ❌ Exception: {str(e)}')
                failed_companies.append({'company': company, 'ticker': ticker, 'error': str(e)})
        else:
            print(f'  ⚠️ No ESG report URL provided')
            failed_companies.append({'company': company, 'ticker': ticker, 'error': 'No ESG report URL'})
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM extracted_kpis')
    after_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f'\n🎯 Processing Summary:')
    print(f'  Companies processed: {len(companies_df)}')
    print(f'  Successful extractions: {len(successful_companies)}')
    print(f'  Failed extractions: {len(failed_companies)}')
    print(f'  KPIs before processing: {before_count}')
    print(f'  KPIs after processing: {after_count}')
    print(f'  New KPIs added: {after_count - before_count}')
    if successful_companies:
        print(f'\n✅ Successful companies:')
        for comp in successful_companies:
            print(f"  {comp['company']}: {comp['kpis_extracted']} extracted, {comp['kpis_saved']} saved")
    if failed_companies:
        print(f'\n❌ Failed companies:')
        for comp in failed_companies:
            print(f"  {comp['company']}: {comp['error']}")
    return len(successful_companies) > 0
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
