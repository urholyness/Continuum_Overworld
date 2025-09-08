
class EnhancedESGDashboardAgent:
    """Agent based on EnhancedESGDashboard from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\dashboard_enhanced.py"""
    
    def __init__(self):
        self.name = "EnhancedESGDashboardAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Enhanced ESG Dashboard with OMG features"""
        """Initialize enhanced dashboard"""
        db_path = self.db_config['database']
        if db_path and (db_path.endswith('.db') or not self.db_config['host']):
            self.db_type = 'sqlite'
            self.db_path = db_path
            print('📱 Using SQLite database:', db_path)
        else:
            self.db_type = 'postgresql'
            print('🐘 Using PostgreSQL database:', self.db_config['database'])
        self.init_session_state()
        try:
            self.extractor = ExtractorClass()
        except Exception as e:
            print(f'⚠️ Could not initialize extractor: {e}')
            self.extractor = None
    def get_db_connection(self):
        """Get database connection"""
        if self.db_type == 'sqlite':
            return sqlite3.connect(self.db_path)
        else:
            if not POSTGRES_AVAILABLE:
                raise ImportError('PostgreSQL required but psycopg2 not installed')
            return psycopg2.connect(**self.db_config)
    def init_session_state(self):
        """Initialize streamlit session state"""
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        if 'progress' not in st.session_state:
            st.session_state.progress = 0
        if 'total_companies' not in st.session_state:
            st.session_state.total_companies = 0
        if 'processed_companies' not in st.session_state:
            st.session_state.processed_companies = 0
        if 'rankings' not in st.session_state:
            st.session_state.rankings = pd.DataFrame()
        if 'processing_log' not in st.session_state:
            st.session_state.processing_log = []
        if 'uploaded_companies' not in st.session_state:
            st.session_state.uploaded_companies = pd.DataFrame()
        if 'process_start_time' not in st.session_state:
            st.session_state.process_start_time = None
    def load_greenwashing_config(self) -> Dict:
        """Load greenwashing configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'greenwashing_config.json')
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f'Error loading greenwashing config: {e}')
            return {}
    def save_greenwashing_config(self, config: Dict) -> bool:
        """Save greenwashing configuration to JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'greenwashing_config.json')
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            st.error(f'Error saving greenwashing config: {e}')
            return False
    def validate_uploaded_csv(self, df: pd.DataFrame) -> bool:
        """Validate uploaded CSV has required columns"""
        required_columns = ['company', 'ticker', 'website']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f'Missing required columns: {missing_columns}')
            return False
        if 'report_years' not in df.columns:
            df['report_years'] = '2024'
            st.info("Added default report_years column with value '2024'")
        return True
    def run_batch_pipeline(self, csv_path: str):
        """Run CSV processing using the simple test processor"""
        try:
            logger.info('Starting CSV processing pipeline')
            st.session_state.processing = True
            st.session_state.progress = 0
            st.session_state.processed_companies = 0
            st.session_state.processing_log = []
            st.session_state.process_start_time = datetime.now()
            processor_script = os.path.join(os.path.dirname(__file__), '..', 'test_csv_processor.py')
            if not os.path.exists(processor_script):
                error_msg = f'CSV processor not found: {processor_script}'
                logger.error(error_msg)
                st.session_state.processing_log.append(error_msg)
                st.session_state.processing = False
                return
            cmd = [sys.executable, processor_script, csv_path]
            log_msg = f"Starting CSV processor: {' '.join(cmd)}"
            logger.info(log_msg)
            st.session_state.processing_log.append(log_msg)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            while process.poll() is None:
                time.sleep(2)
                if st.session_state.progress < 90:
                    st.session_state.progress += 10
                try:
                    if process.stdout:
                        line = process.stdout.readline()
                        if line.strip():
                            st.session_state.processing_log.append(f'Processor: {line.strip()}')
                            logger.info(f'Processor output: {line.strip()}')
                except:
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                st.session_state.progress = 100
                success_msg = 'CSV processing completed successfully!'
                st.session_state.processing_log.append(success_msg)
                logger.info(success_msg)
                if stdout.strip():
                    st.session_state.processing_log.append(f'Output: {stdout.strip()}')
            else:
                error_msg = f'Processing failed: {stderr}'
                st.session_state.processing_log.append(error_msg)
                logger.error(error_msg)
        except Exception as e:
            error_msg = f'Pipeline error: {str(e)}'
            st.session_state.processing_log.append(error_msg)
            logger.error(error_msg, exc_info=True)
            st.session_state.processing = False
        finally:
            st.session_state.processing = False
            logger.info('Pipeline thread completed')
    def process_companies_with_progress(self, companies_df):
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
    def update_progress_from_db(self):
        """Update progress by checking database records with enhanced logging"""
        try:
            query = "\n            SELECT COUNT(DISTINCT company) as count \n            FROM extracted_kpis_enhanced \n            WHERE created_at > NOW() - INTERVAL '1 hour'\n            "
            result = pd.read_sql(query, self.engine)
            processed = result.iloc[0]['count'] if not result.empty else 0
            old_processed = st.session_state.processed_companies
            st.session_state.processed_companies = processed
            if st.session_state.total_companies > 0:
                old_progress = st.session_state.progress
                st.session_state.progress = min(100, int(processed / st.session_state.total_companies * 100))
                if processed != old_processed or st.session_state.progress != old_progress:
                    logger.info(f'Progress update: {processed}/{st.session_state.total_companies} companies ({st.session_state.progress}%)')
            elif processed > 0:
                st.session_state.progress = min(50, processed * 10)
                logger.info(f'Progress estimate: {processed} companies processed, estimated {st.session_state.progress}%')
        except Exception as e:
            logger.warning(f'Error updating progress from database: {e}')
    def load_live_rankings(self) -> pd.DataFrame:
        """Load live rankings from database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            if self.db_type == 'sqlite':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='extracted_kpis'")
            else:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name='extracted_kpis'")
            table_exists = cursor.fetchone() is not None
            cursor.close()
            if not table_exists:
                conn.close()
                return pd.DataFrame()
            if self.db_type == 'sqlite':
                query = "\n                SELECT \n                    k.company,\n                    k.ticker,\n                    COUNT(DISTINCT k.kpi_name) as total_kpis,\n                    AVG(k.confidence_score) as avg_confidence,\n                    0 as greenwashing_score,\n                    MAX(k.created_at) as last_updated,\n                    k.kpi_year\n                FROM extracted_kpis k\n                WHERE k.created_at > datetime('now', '-30 days')\n                GROUP BY k.company, k.ticker, k.kpi_year\n                ORDER BY total_kpis DESC, avg_confidence DESC\n                "
            else:
                query = "\n                SELECT \n                    k.company,\n                    k.ticker,\n                    COUNT(DISTINCT k.kpi_name) as total_kpis,\n                    AVG(k.confidence_score) as avg_confidence,\n                    0 as greenwashing_score,\n                    MAX(k.created_at) as last_updated,\n                    k.kpi_year\n                FROM extracted_kpis k\n                WHERE k.created_at > NOW() - INTERVAL '30 days'\n                GROUP BY k.company, k.ticker, k.kpi_year\n                ORDER BY total_kpis DESC, avg_confidence DESC\n                "
            conn = self.get_db_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            if not df.empty:
                df['blended_score'] = df['avg_confidence'] * 0.6 + (100 - df['greenwashing_score']) * 0.4
                df['blended_score'] = df['blended_score'].fillna(0)
                df['last_updated'] = pd.to_datetime(df['last_updated']).dt.strftime('%H:%M:%S')
                df['avg_confidence'] = df['avg_confidence'].round(3)
                df['greenwashing_score'] = df['greenwashing_score'].round(1)
                df['blended_score'] = df['blended_score'].round(1)
                df['rank'] = df['blended_score'].rank(method='dense', ascending=False).astype(int)
                df = df.sort_values('rank')
            return df
        except Exception as e:
            st.error(f'Error loading live rankings: {e}')
            return pd.DataFrame()
    def display_upload_initiate_tab(self):
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
    def display_live_rankings_tab(self):
        """Display Live Rankings tab"""
        st.header('📊 Live Rankings')
        if st.session_state.processing:
            progress_col1, progress_col2 = st.columns(2)
            with progress_col1:
                st.metric('Progress', f'{st.session_state.progress}%')
                progress_bar = st.progress(st.session_state.progress / 100)
            with progress_col2:
                st.metric('Processed', f'{st.session_state.processed_companies}/{st.session_state.total_companies}')
                if st.session_state.processing_log:
                    st.text('Status: ' + st.session_state.processing_log[-1][-50:])
            if st.session_state.process_start_time:
                elapsed = datetime.now() - st.session_state.process_start_time
                st.info(f'⏱️ Processing time: {elapsed}')
            time.sleep(3)
            st.rerun()
        with st.spinner('Loading live rankings...'):
            rankings_df = self.load_live_rankings()
        if not rankings_df.empty:
            st.subheader('🏆 Current Rankings')
            if len(rankings_df) >= 3:
                top3_col1, top3_col2, top3_col3 = st.columns(3)
                with top3_col1:
                    st.markdown('🥇 **1st Place**')
                    st.metric(rankings_df.iloc[0]['company'], f"{rankings_df.iloc[0]['blended_score']:.1f}")
                with top3_col2:
                    st.markdown('🥈 **2nd Place**')
                    st.metric(rankings_df.iloc[1]['company'], f"{rankings_df.iloc[1]['blended_score']:.1f}")
                with top3_col3:
                    st.markdown('🥉 **3rd Place**')
                    st.metric(rankings_df.iloc[2]['company'], f"{rankings_df.iloc[2]['blended_score']:.1f}")
            st.dataframe(rankings_df, use_container_width=True, column_config={'rank': 'Rank', 'company': 'Company', 'ticker': 'Ticker', 'total_kpis': 'KPIs', 'avg_confidence': 'Confidence', 'greenwashing_score': 'GW Risk', 'blended_score': 'Score', 'last_updated': 'Updated', 'kpi_year': 'Year'})
            if len(rankings_df) > 1:
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.bar(rankings_df.head(10), x='company', y='blended_score', title='Top 10 Companies by Blended Score', color='blended_score', color_continuous_scale='viridis')
                    fig1.update_xaxes(tickangle=45)
                    st.plotly_chart(fig1, use_container_width=True)
                with col2:
                    fig2 = px.scatter(rankings_df, x='avg_confidence', y='greenwashing_score', size='total_kpis', hover_data=['company'], title='Confidence vs Greenwashing Risk', color='blended_score', color_continuous_scale='RdYlGn_r')
                    st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info('No recent data available. Upload companies and run the pipeline to see live rankings.')
        if st.button('🔄 Refresh Rankings'):
            st.rerun()
    def display_json_editor_tab(self):
        """Display JSON Editor tab"""
        st.header('⚙️ Edit Greenwashing Methodology')
        config = self.load_greenwashing_config()
        if config:
            st.subheader('📝 Configuration Editor')
            edited_json = st.text_area('Greenwashing Configuration (JSON)', value=json.dumps(config, indent=4), height=400, help='Edit the greenwashing analysis configuration. Changes will be applied immediately.')
            col1, col2 = st.columns(2)
            with col1:
                if st.button('💾 Save & Reload', type='primary'):
                    try:
                        new_config = json.loads(edited_json)
                        if self.save_greenwashing_config(new_config):
                            st.success('✅ Configuration saved successfully!')
                            st.info('Changes will take effect for new analysis runs.')
                        else:
                            st.error('❌ Failed to save configuration')
                    except json.JSONDecodeError as e:
                        st.error(f'❌ Invalid JSON: {e}')
            with col2:
                if st.button('🔄 Reset to Default'):
                    default_config = {'indicators': {'vagueness': {'patterns': ['committed to', 'striving for', 'working towards'], 'threshold': 0.05}, 'contradictions': {'zero_claims': ['zero emissions', 'carbon neutral', 'net zero']}, 'sentiment_imbalance': {'positive_threshold': 0.3, 'risk_mentions_min': 0.01}, 'omissions': {'required_categories': ['scope 1', 'scope 2', 'scope 3', 'governance']}, 'hype': {'keywords': ['revolutionary', 'game-changing', 'unprecedented'], 'threshold': 5}}, 'weights': {'vagueness': 0.25, 'contradictions': 0.3, 'sentiment_imbalance': 0.2, 'omissions': 0.15, 'hype': 0.1}, 'thresholds': {'low': 25, 'medium': 50, 'high': 75}}
                    if self.save_greenwashing_config(default_config):
                        st.success('✅ Configuration reset to default!')
                        st.rerun()
            st.subheader('📊 Current Configuration Summary')
            col1, col2 = st.columns(2)
            with col1:
                st.write('**Indicator Weights:**')
                weights = config.get('weights', {})
                for indicator, weight in weights.items():
                    st.write(f'- {indicator}: {weight}')
            with col2:
                st.write('**Risk Thresholds:**')
                thresholds = config.get('thresholds', {})
                for level, threshold in thresholds.items():
                    st.write(f'- {level}: {threshold}')
        else:
            st.error('Unable to load greenwashing configuration file.')
    def display_charts_analysis_tab(self):
        """Display Charts & Analysis tab"""
        st.header('📈 Charts & Analysis')
        try:
            kpi_df = self.load_kpi_data()
            if kpi_df.empty:
                st.info('No KPI data available for analysis. Upload companies and run the pipeline first.')
                return
        except Exception as e:
            st.error(f'Error loading KPI data: {e}')
            st.info('No data available for analysis. Upload companies and run the pipeline first.')
            return
        if not kpi_df.empty:
            st.subheader('📊 Multi-Year Trends')
            companies = sorted(kpi_df['company'].unique())
            selected_companies = st.multiselect('Select Companies', companies, default=companies[:5])
            if selected_companies:
                filtered_kpi = kpi_df[kpi_df['company'].isin(selected_companies)]
                env_kpis = filtered_kpi[filtered_kpi['kpi_name'].str.contains('carbon|energy|renewable', case=False, na=False)]
                if not env_kpis.empty:
                    yearly_env = env_kpis.groupby(['company', 'kpi_year', 'kpi_name'])['kpi_value'].mean().reset_index()
                    fig = px.line(yearly_env, x='kpi_year', y='kpi_value', color='company', facet_col='kpi_name', title='Environmental KPIs Over Time')
                    st.plotly_chart(fig, use_container_width=True)
                confidence_data = filtered_kpi.groupby(['company', 'kpi_year'])['confidence_score'].mean().reset_index()
                if not confidence_data.empty:
                    fig2 = px.line(confidence_data, x='kpi_year', y='confidence_score', color='company', title='KPI Extraction Confidence Over Time')
                    fig2.update_yaxis(range=[0, 1], title='Confidence Score')
                    st.plotly_chart(fig2, use_container_width=True)
                st.subheader('📊 KPI Distribution')
                kpi_counts = filtered_kpi.groupby(['company', 'kpi_name']).size().reset_index(name='count')
                if not kpi_counts.empty:
                    fig3 = px.bar(kpi_counts.groupby('company')['count'].sum().reset_index(), x='company', y='count', title='Total KPIs Extracted by Company')
                    st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info('No data available for analysis. Upload companies and run the pipeline first.')
    def load_kpi_data(self) -> pd.DataFrame:
        """Load KPI data from database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            if self.db_type == 'sqlite':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='extracted_kpis'")
            else:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name='extracted_kpis'")
            table_exists = cursor.fetchone() is not None
            cursor.close()
            if not table_exists:
                conn.close()
                return pd.DataFrame()
            query = '\n                SELECT * FROM extracted_kpis \n                ORDER BY created_at DESC\n            '
            df = pd.read_sql(query, conn)
            conn.close()
            if not df.empty and 'kpi_year' in df.columns:
                df['kpi_year'] = df['kpi_year'].fillna(2024)
            if not df.empty:
                def safe_json_parse(json_str):
                    if pd.isna(json_str) or json_str is None:
                        return {}
                    try:
                        if isinstance(json_str, str):
                            return json.loads(json_str)
                        elif isinstance(json_str, dict):
                            return json_str
                        else:
                            return {}
                    except (json.JSONDecodeError, TypeError):
                        return {}
                df['indicator_scores'] = df['indicator_scores'].apply(safe_json_parse)
                df['flagged_sections'] = df['flagged_sections'].apply(safe_json_parse)
                if 'analysis_year' in df.columns:
                    df['analysis_year'] = df['analysis_year'].fillna(2024)
            return df
        except Exception as e:
            st.error(f'Error loading KPI data: {e}')
            return pd.DataFrame()
    def load_greenwashing_data(self) -> pd.DataFrame:
        """Load greenwashing analysis data with safe JSON parsing"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            if self.db_type == 'sqlite':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='greenwashing_analysis'")
            else:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name='greenwashing_analysis'")
            table_exists = cursor.fetchone() is not None
            cursor.close()
            if not table_exists:
                conn.close()
                return pd.DataFrame()
            query = '\n                SELECT company, ticker, overall_score, indicator_scores, \n                       flagged_sections, report_name, analysis_year, analysis_date\n                FROM greenwashing_analysis \n                ORDER BY analysis_date DESC\n            '
            df = pd.read_sql(query, conn)
            conn.close()
            def safe_json_load(data):
                if isinstance(data, str):
                    return json.loads(data)
                elif isinstance(data, dict):
                    return data
                return {}
            if not df.empty:
                def safe_json_parse(json_str):
                    if pd.isna(json_str) or json_str is None:
                        return {}
                    try:
                        if isinstance(json_str, str):
                            return json.loads(json_str)
                        elif isinstance(json_str, dict):
                            return json_str
                        else:
                            return {}
                    except (json.JSONDecodeError, TypeError):
                        return {}
                df['indicator_scores'] = df['indicator_scores'].apply(safe_json_parse)
                df['flagged_sections'] = df['flagged_sections'].apply(safe_json_parse)
                if 'analysis_year' in df.columns:
                    df['analysis_year'] = df['analysis_year'].fillna(2024)
            return df
        except Exception as e:
            st.error(f'Error loading greenwashing data: {e}')
            return pd.DataFrame()
    def run(self):
        """Run the enhanced dashboard"""
        st.sidebar.markdown('<div class="sidebar-section"><h2>🚀 ESG Analytics</h2></div>', unsafe_allow_html=True)
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            st.sidebar.image(logo_path, width=200)
        elif st.session_state.dark_mode:
            st.sidebar.markdown('### 🌟 **ESG AI Analytics**')
        else:
            st.sidebar.markdown('### 🌱 **ESG Analytics**')
        new_dark_mode = st.sidebar.checkbox('🌙 Dark Mode', value=st.session_state.dark_mode)
        if new_dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = new_dark_mode
            st.rerun()
        if st.session_state.dark_mode:
            st.markdown('<h1 class="main-header">🚀 ESG KPI MVP 2.0 - OMG Dashboard</h1>', unsafe_allow_html=True)
        else:
            st.markdown('<h1 class="main-header">🌱 ESG KPI MVP 2.0 - OMG Dashboard</h1>', unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(['📤 Upload & Initiate', '📊 Live Rankings', '📈 Charts & Analysis', '⚙️ Edit Methodology'])
        with tab1:
            self.display_upload_initiate_tab()
        with tab2:
            self.display_live_rankings_tab()
        with tab3:
            self.display_charts_analysis_tab()
        with tab4:
            self.display_json_editor_tab()
        st.sidebar.markdown('---')
        st.sidebar.markdown('**ESG KPI MVP 2.0 - OMG Edition**')
        st.sidebar.markdown('Complete ESG analytics with live processing')
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
