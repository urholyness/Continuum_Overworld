
class check_processing_performanceAgent:
    """Agent based on check_processing_performance from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\health_checker.py"""
    
    def __init__(self):
        self.name = "check_processing_performanceAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
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
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
