
class display_upload_initiate_tabAgent:
    """Agent based on display_upload_initiate_tab from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\dashboard_enhanced.py"""
    
    def __init__(self):
        self.name = "display_upload_initiate_tabAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Display Upload & Initiate tab"""
    st.header('📤 Upload & Initiate Pipeline')
    uploaded_file = st.file_uploader('Upload Companies CSV/XLSX', type=['csv', 'xlsx'], help='File must contain columns: company, ticker, website. Optional: report_years (comma-separated)')
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                companies_df = pd.read_csv(uploaded_file)
            else:
                companies_df = pd.read_excel(uploaded_file)
            if self.validate_uploaded_csv(companies_df):
                st.session_state.uploaded_companies = companies_df
                st.subheader('📋 Preview')
                st.dataframe(companies_df.head(10))
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric('Total Companies', len(companies_df))
                with col2:
                    total_years = companies_df['report_years'].str.split(',').apply(len).sum()
                    st.metric('Total Company-Years', total_years)
                with col3:
                    unique_years = set()
                    for years in companies_df['report_years']:
                        unique_years.update(years.split(','))
                    st.metric('Unique Years', len(unique_years))
                if st.button('🚀 Initiate Pipeline', type='primary', disabled=st.session_state.processing):
                    if not st.session_state.processing:
                        st.session_state.processing = True
                        st.session_state.total_companies = len(companies_df)
                        st.session_state.progress = 0
                        st.session_state.processed_companies = 0
                        st.session_state.current_company = ''
                        st.session_state.process_start_time = datetime.now()
                        st.session_state.processing_log = []
                        self.process_companies_with_progress(companies_df)
                        st.success('Processing started! Watch the progress below.')
                        st.rerun()
        except Exception as e:
            st.error(f'Error processing file: {e}')
    if st.session_state.processing:
        st.markdown('### 🔄 Processing in Progress')
        progress_value = st.session_state.progress / 100 if st.session_state.progress > 0 else 0
        st.progress(progress_value, f'Progress: {st.session_state.progress}%')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric('📊 Progress', f'{st.session_state.progress}%')
        with col2:
            st.metric('🏢 Processed', f'{st.session_state.processed_companies}/{st.session_state.total_companies}')
        with col3:
            current_company = getattr(st.session_state, 'current_company', 'Initializing...')
            st.metric('🔄 Current', current_company[:15] + '...' if len(current_company) > 15 else current_company)
        with col4:
            if st.session_state.process_start_time:
                elapsed = datetime.now() - st.session_state.process_start_time
                elapsed_str = f'{elapsed.seconds // 60}m {elapsed.seconds % 60}s'
                st.metric('⏱️ Elapsed', elapsed_str)
        if hasattr(st.session_state, 'processing_log') and st.session_state.processing_log:
            st.subheader('📝 Live Processing Log')
            log_text = '\\n'.join(st.session_state.processing_log[-5:])
            st.text_area('Recent Activity', log_text, height=100, disabled=True)
        time.sleep(2)
        st.rerun()
    elif st.session_state.progress > 0:
        st.markdown(f'<div class="metric-card success-card"><strong>✅ Last pipeline completed successfully!</strong><br>Processed: {st.session_state.processed_companies}/{st.session_state.total_companies} companies</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-card"><strong>📤 Ready to process</strong><br>Upload a CSV file to begin KPI extraction</div>', unsafe_allow_html=True)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
