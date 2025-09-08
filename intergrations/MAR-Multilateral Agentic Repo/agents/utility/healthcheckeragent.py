
class HealthCheckerAgent:
    """Agent based on HealthChecker from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\health_checker.py"""
    
    def __init__(self):
        self.name = "HealthCheckerAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Comprehensive health checking for all system components"""
        self.load_environment()
    def load_environment(self):
        """Load environment variables from .env file if it exists"""
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and (not line.startswith('#')) and ('=' in line):
                        key, value = line.split('=', 1)
                        os.environ[key] = value.strip('"\'')
    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        logger.info('🗄️  Checking database health...')
        try:
            start_time = time.time()
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            cursor.execute("\n                SELECT table_name FROM information_schema.tables \n                WHERE table_schema = 'public' \n                AND table_name IN ('extracted_kpis_enhanced', 'greenwashing_analysis')\n            ")
            tables = [row[0] for row in cursor.fetchall()]
            record_counts = {}
            for table in ['extracted_kpis_enhanced', 'greenwashing_analysis']:
                if table in tables:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    record_counts[table] = cursor.fetchone()[0]
                else:
                    record_counts[table] = 'Table missing'
            cursor.execute("\n                SELECT COUNT(*) FROM extracted_kpis_enhanced \n                WHERE created_at > NOW() - INTERVAL '24 hours'\n            ")
            recent_activity = cursor.fetchone()[0]
            response_time = time.time() - start_time
            cursor.close()
            conn.close()
            status = 'healthy'
            if response_time > 5.0:
                status = 'slow'
            elif not tables:
                status = 'tables_missing'
            return {'status': status, 'response_time_ms': round(response_time * 1000, 2), 'tables_found': tables, 'record_counts': record_counts, 'recent_activity_24h': recent_activity, 'last_check': datetime.now().isoformat()}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e), 'error_type': type(e).__name__, 'last_check': datetime.now().isoformat()}
    def check_document_ai(self) -> Dict[str, Any]:
        """Check Document AI API health"""
        logger.info('🤖 Checking Document AI health...')
        try:
            from google.cloud import documentai_v1 as documentai
            from google.api_core import exceptions as gcp_exceptions
            required_vars = ['GOOGLE_APPLICATION_CREDENTIALS', 'GOOGLE_CLOUD_PROJECT_ID', 'DOCUMENT_AI_PROCESSOR_ID']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                return {'status': 'misconfigured', 'error': f'Missing environment variables: {missing_vars}', 'last_check': datetime.now().isoformat()}
            creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not os.path.exists(creds_path):
                return {'status': 'credentials_missing', 'error': f'Credentials file not found: {creds_path}', 'last_check': datetime.now().isoformat()}
            start_time = time.time()
            client = documentai.DocumentProcessorServiceClient()
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
            location = os.getenv('DOCUMENT_AI_LOCATION', 'us')
            processor_id = os.getenv('DOCUMENT_AI_PROCESSOR_ID')
            processor_name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'
            try:
                processor = client.get_processor(name=processor_name)
                response_time = time.time() - start_time
                return {'status': 'healthy', 'response_time_ms': round(response_time * 1000, 2), 'processor_name': processor.display_name, 'processor_type': processor.type_, 'processor_state': processor.state.name, 'project_id': project_id, 'location': location, 'last_check': datetime.now().isoformat()}
            except gcp_exceptions.PermissionDenied as e:
                return {'status': 'permission_denied', 'error': 'Service account lacks Document AI permissions', 'details': str(e), 'required_roles': ['Document AI API User', 'Document AI API Admin'], 'last_check': datetime.now().isoformat()}
            except gcp_exceptions.NotFound as e:
                return {'status': 'processor_not_found', 'error': f'Processor not found: {processor_name}', 'details': str(e), 'last_check': datetime.now().isoformat()}
        except ImportError as e:
            return {'status': 'library_missing', 'error': 'Google Cloud Document AI library not installed', 'install_command': 'pip install google-cloud-documentai', 'details': str(e), 'last_check': datetime.now().isoformat()}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'error_type': type(e).__name__, 'last_check': datetime.now().isoformat()}
    def check_gemini(self) -> Dict[str, Any]:
        """Check Gemini API health"""
        logger.info('💎 Checking Gemini API health...')
        try:
            import google.generativeai as genai
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return {'status': 'api_key_missing', 'error': 'GEMINI_API_KEY environment variable not set', 'last_check': datetime.now().isoformat()}
            genai.configure(api_key=api_key)
            start_time = time.time()
            model = genai.GenerativeModel('gemini-pro')
            try:
                response = model.generate_content('Test connection')
                response_time = time.time() - start_time
                return {'status': 'healthy', 'response_time_ms': round(response_time * 1000, 2), 'model': 'gemini-pro', 'response_length': len(response.text) if response.text else 0, 'last_check': datetime.now().isoformat()}
            except Exception as e:
                if 'API_KEY' in str(e).upper():
                    return {'status': 'invalid_api_key', 'error': 'Invalid or expired API key', 'details': str(e), 'last_check': datetime.now().isoformat()}
                else:
                    return {'status': 'api_error', 'error': str(e), 'error_type': type(e).__name__, 'last_check': datetime.now().isoformat()}
        except ImportError as e:
            return {'status': 'library_missing', 'error': 'Google Generative AI library not installed', 'install_command': 'pip install google-generativeai', 'details': str(e), 'last_check': datetime.now().isoformat()}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'error_type': type(e).__name__, 'last_check': datetime.now().isoformat()}
    def check_processing_performance(self) -> Dict[str, Any]:
        """Check recent processing performance"""
        logger.info('📊 Checking processing performance...')
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("\n                SELECT COUNT(DISTINCT company) \n                FROM extracted_kpis_enhanced \n                WHERE created_at > NOW() - INTERVAL '1 hour'\n            ")
            recent_companies = cursor.fetchone()[0]
            cursor.execute("\n                SELECT COUNT(*) \n                FROM extracted_kpis_enhanced \n                WHERE created_at > NOW() - INTERVAL '24 hours'\n            ")
            recent_kpis = cursor.fetchone()[0]
            cursor.execute("\n                SELECT \n                    COUNT(*) FILTER (WHERE confidence_score > 0.5) * 100.0 / NULLIF(COUNT(*), 0) as success_rate\n                FROM extracted_kpis_enhanced\n                WHERE created_at > NOW() - INTERVAL '24 hours'\n            ")
            result = cursor.fetchone()
            success_rate = float(result[0]) if result[0] is not None else 0.0
            cursor.execute("\n                SELECT extraction_method, COUNT(*) \n                FROM extracted_kpis_enhanced \n                WHERE created_at > NOW() - INTERVAL '24 hours'\n                GROUP BY extraction_method\n            ")
            method_distribution = dict(cursor.fetchall())
            cursor.execute("\n                SELECT AVG(overall_score) \n                FROM greenwashing_analysis \n                WHERE analysis_date > NOW() - INTERVAL '24 hours'\n            ")
            result = cursor.fetchone()
            avg_greenwashing_score = float(result[0]) if result[0] is not None else 0.0
            cursor.close()
            conn.close()
            status = 'healthy'
            if success_rate < 50:
                status = 'poor_quality'
            elif recent_companies == 0:
                status = 'no_recent_activity'
            elif success_rate < 70:
                status = 'degraded'
            return {'status': status, 'companies_last_hour': recent_companies, 'kpis_last_24h': recent_kpis, 'success_rate_percentage': round(success_rate, 2), 'avg_greenwashing_score': round(avg_greenwashing_score, 2), 'extraction_methods': method_distribution, 'last_check': datetime.now().isoformat()}
        except Exception as e:
            return {'status': 'check_failed', 'error': str(e), 'error_type': type(e).__name__, 'last_check': datetime.now().isoformat()}
    def full_health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        logger.info('🏥 Running comprehensive health check...')
        start_time = time.time()
        components = {'database': self.check_database(), 'document_ai': self.check_document_ai(), 'gemini': self.check_gemini(), 'processing': self.check_processing_performance()}
        component_statuses = [comp['status'] for comp in components.values()]
        if all((status == 'healthy' for status in component_statuses)):
            overall_status = 'healthy'
        elif any((status in ['unhealthy', 'error', 'misconfigured'] for status in component_statuses)):
            overall_status = 'unhealthy'
        else:
            overall_status = 'degraded'
        total_time = time.time() - start_time
        return {'timestamp': datetime.now().isoformat(), 'overall_status': overall_status, 'check_duration_seconds': round(total_time, 2), 'components': components, 'summary': self.generate_summary(components)}
    def generate_summary(self, components: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate a summary of health check results"""
        healthy_count = sum((1 for comp in components.values() if comp['status'] == 'healthy'))
        total_count = len(components)
        issues = []
        for name, comp in components.items():
            if comp['status'] != 'healthy':
                issues.append(f"{name}: {comp['status']}")
        return {'healthy_components': healthy_count, 'total_components': total_count, 'health_percentage': round(healthy_count / total_count * 100, 1), 'issues': issues}
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
