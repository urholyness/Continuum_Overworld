
class ConfigAgent:
    """Agent based on Config from ..\Orion\config\environments\env_config.py"""
    
    def __init__(self):
        self.name = "ConfigAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Central configuration management"""
        self.api = APIConfig(openai_api_key=os.getenv('OPENAI_API_KEY', ''), openai_model=os.getenv('OPENAI_MODEL', 'gpt-4'), gmail_credentials_path=os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json'), gmail_token_path=os.getenv('GMAIL_TOKEN_PATH', 'token.json'))
        self.database = DatabaseConfig(db_url=os.getenv('DATABASE_URL', 'sqlite:///farm5_agents.db'), db_name=os.getenv('DB_NAME', 'farm5_agents'), connection_pool_size=int(os.getenv('DB_POOL_SIZE', '10')), echo_sql=os.getenv('DB_ECHO_SQL', 'false').lower() == 'true')
        self.agent = AgentConfig(max_retries=int(os.getenv('AGENT_MAX_RETRIES', '3')), retry_delay=int(os.getenv('AGENT_RETRY_DELAY', '5')), task_timeout=int(os.getenv('AGENT_TASK_TIMEOUT', '300')), approval_timeout=int(os.getenv('AGENT_APPROVAL_TIMEOUT', '3600')), batch_size=int(os.getenv('AGENT_BATCH_SIZE', '10')), rate_limit_per_minute=int(os.getenv('AGENT_RATE_LIMIT', '60')))
        self.monitoring = MonitoringConfig(enable_monitoring=os.getenv('ENABLE_MONITORING', 'true').lower() == 'true', metrics_endpoint=os.getenv('METRICS_ENDPOINT'), alert_email=os.getenv('ALERT_EMAIL'), slack_webhook=os.getenv('SLACK_WEBHOOK'), log_level=os.getenv('LOG_LEVEL', 'INFO'), log_retention_days=int(os.getenv('LOG_RETENTION_DAYS', '30')))
        self.agent_configs = self._load_agent_configs()
    def _load_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load agent-specific configurations from file or environment"""
        config_path = os.getenv('AGENT_CONFIG_PATH', 'agent_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {'email_manager_001': {'auto_reply_threshold': 0.85, 'classification_model': 'gpt-4', 'max_emails_per_batch': 50, 'enable_auto_responses': True}, 'sales_agent_001': {'outreach_daily_limit': 100, 'follow_up_days': [3, 7, 14, 30], 'lead_scoring_threshold': 70, 'personalization_level': 'high'}, 'research_agent_001': {'research_depth': 'comprehensive', 'sources_per_query': 10, 'fact_check_enabled': True, 'update_frequency_hours': 24}, 'support_agent_001': {'auto_assign_tickets': True, 'priority_keywords': ['urgent', 'critical', 'broken', 'down'], 'response_time_sla_minutes': 60, 'escalation_threshold': 3}, 'finance_agent_001': {'invoice_approval_required': True, 'expense_categories': ['tools', 'marketing', 'operations', 'personnel'], 'budget_alert_threshold': 0.8, 'payment_terms_days': 30}, 'analytics_agent_001': {'dashboard_refresh_minutes': 15, 'anomaly_detection_enabled': True, 'report_formats': ['pdf', 'excel', 'json'], 'visualization_library': 'plotly'}, 'growth_agent_001': {'review_frequency': 'weekly', 'optimization_threshold': 0.7, 'strategy_planning_horizon_days': 90, 'agent_performance_window_days': 7}}
    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """Get configuration for specific agent"""
        return self.agent_configs.get(agent_id, {})
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        if not self.api.openai_api_key:
            errors.append('OPENAI_API_KEY is required')
        if not os.path.exists(self.api.gmail_credentials_path):
            errors.append(f'Gmail credentials file not found: {self.api.gmail_credentials_path}')
        if self.database.db_url.startswith('sqlite://') and (not os.path.exists('data')):
            os.makedirs('data', exist_ok=True)
        if errors:
            for error in errors:
                print(f'Configuration Error: {error}')
            return False
        return True
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {'api': {'openai_model': self.api.openai_model, 'gmail_scopes': self.api.gmail_scopes}, 'database': {'db_url': self.database.db_url.split('://')[0] + '://***', 'db_name': self.database.db_name, 'connection_pool_size': self.database.connection_pool_size}, 'agent': {'max_retries': self.agent.max_retries, 'retry_delay': self.agent.retry_delay, 'task_timeout': self.agent.task_timeout, 'batch_size': self.agent.batch_size, 'rate_limit_per_minute': self.agent.rate_limit_per_minute}, 'monitoring': {'enable_monitoring': self.monitoring.enable_monitoring, 'log_level': self.monitoring.log_level, 'log_retention_days': self.monitoring.log_retention_days}}
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
