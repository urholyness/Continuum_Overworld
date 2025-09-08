
class process_companies_with_progressAgent:
    """Agent based on process_companies_with_progress from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\dashboard_enhanced.py"""
    
    def __init__(self):
        self.name = "process_companies_with_progressAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Process companies with real-time progress updates"""
    try:
        total_companies = len(companies_df)
        if not self.extractor:
            self.extractor = ExtractorClass()
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        log_placeholder = st.empty()
        for index, row in companies_df.iterrows():
            company = row['company']
            ticker = row['ticker']
            st.session_state.current_company = company
            st.session_state.processed_companies = index
            progress_percent = int(index / total_companies * 100)
            st.session_state.progress = progress_percent
            progress_placeholder.progress(progress_percent / 100, f'Processing {index + 1}/{total_companies}: {company}')
            status_placeholder.info(f'🔄 Currently processing: **{company}** ({ticker})')
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] Processing {company}..."
            st.session_state.processing_log.append(log_entry)
            log_placeholder.text_area('Processing Log', '\\n'.join(st.session_state.processing_log[-10:]), height=150)
            esg_url = row.get('esg_report_url', '')
            if esg_url:
                try:
                    start_msg = f'🔄 Starting extraction from: {esg_url}'
                    st.session_state.processing_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {start_msg}")
                    log_placeholder.text_area('Processing Log', '\\n'.join(st.session_state.processing_log[-10:]), height=150)
                    result = self.extractor.process_pdf_url(company, ticker, esg_url)
                    if result.success:
                        success_msg = f'✅ {company}: {len(result.kpis_extracted)} KPIs extracted in {result.processing_time:.1f}s'
                        st.session_state.processing_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {success_msg}")
                        conn = self.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('SELECT COUNT(*) FROM extracted_kpis WHERE company = ? AND ticker = ?', (company, ticker))
                        saved_count = cursor.fetchone()[0]
                        cursor.close()
                        conn.close()
                        db_msg = f'💾 {company}: {saved_count} KPIs saved to database'
                        st.session_state.processing_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {db_msg}")
                    else:
                        error_msg = f'❌ {company}: {result.error_message}'
                        st.session_state.processing_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
                except Exception as e:
                    error_msg = f'❌ {company}: Error - {str(e)}'
                    st.session_state.processing_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
                    logger.error(f'Processing error for {company}: {e}', exc_info=True)
            else:
                skip_msg = f'⚠️ {company}: No ESG report URL provided'
                st.session_state.processing_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {skip_msg}")
            log_placeholder.text_area('Processing Log', '\\n'.join(st.session_state.processing_log[-10:]), height=150)
            time.sleep(1)
        st.session_state.processing = False
        st.session_state.progress = 100
        st.session_state.processed_companies = total_companies
        progress_placeholder.progress(1.0, f'✅ Completed! Processed {total_companies} companies')
        status_placeholder.success(f'🎉 Processing complete! Check Live Rankings for results.')
        completion_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 Pipeline completed! All {total_companies} companies processed."
        st.session_state.processing_log.append(completion_msg)
        log_placeholder.text_area('Processing Log', '\\n'.join(st.session_state.processing_log[-10:]), height=150)
    except Exception as e:
        st.session_state.processing = False
        error_msg = f'Pipeline error: {str(e)}'
        st.error(error_msg)
        logger.error(error_msg, exc_info=True)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
