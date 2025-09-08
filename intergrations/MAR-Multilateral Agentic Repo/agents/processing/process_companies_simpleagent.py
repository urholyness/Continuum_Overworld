
class process_companies_simpleAgent:
    """Agent based on process_companies_simple from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\dashboard_working.py"""
    
    def __init__(self):
        self.name = "process_companies_simpleAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Simple, working processing function"""
    if st.session_state.processing:
        st.warning('Processing already in progress...')
        return
    st.session_state.processing = True
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_area = st.empty()
    results = []
    try:
        for index, row in companies_df.iterrows():
            company = row['company']
            ticker = row['ticker']
            esg_url = row.get('esg_report_url', '')
            progress = (index + 1) / len(companies_df)
            progress_bar.progress(progress)
            status_text.info(f'Processing {index + 1}/{len(companies_df)}: {company}')
            if esg_url:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM extracted_kpis WHERE company = ? AND ticker = ?', (company, ticker))
                    before_count = cursor.fetchone()[0]
                    cursor.close()
                    conn.close()
                    result = st.session_state.extractor.process_pdf_url(company, ticker, esg_url)
                    if result.success:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('SELECT COUNT(*) FROM extracted_kpis WHERE company = ? AND ticker = ?', (company, ticker))
                        after_count = cursor.fetchone()[0]
                        cursor.close()
                        conn.close()
                        new_kpis = after_count - before_count
                        results.append({'company': company, 'status': f'✅ Success: {new_kpis} new KPIs', 'total_kpis': after_count, 'processing_time': f'{result.processing_time:.1f}s'})
                    else:
                        results.append({'company': company, 'status': f'❌ Failed: {result.error_message}', 'total_kpis': 0, 'processing_time': '0s'})
                except Exception as e:
                    results.append({'company': company, 'status': f'💥 Error: {str(e)}', 'total_kpis': 0, 'processing_time': '0s'})
            else:
                results.append({'company': company, 'status': '⚠️ No ESG URL provided', 'total_kpis': 0, 'processing_time': '0s'})
            if results:
                results_df = pd.DataFrame(results)
                results_area.dataframe(results_df)
        progress_bar.progress(1.0)
        status_text.success('✅ Processing completed!')
        if results:
            st.subheader('📊 Processing Results')
            final_results = pd.DataFrame(results)
            st.dataframe(final_results)
            successful = len([r for r in results if 'Success' in r['status']])
            st.metric('Successful Extractions', f'{successful}/{len(results)}')
    finally:
        st.session_state.processing = False
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
