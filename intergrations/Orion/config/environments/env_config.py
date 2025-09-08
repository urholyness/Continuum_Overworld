# Farm 5.0 - Environment Configuration and Setup
# config.py

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

@dataclass
class APIConfig:
    """Configuration for external APIs"""
    openai_api_key: str
    openai_model: str = "gpt-4"
    gmail_credentials_path: str = "credentials.json"
    gmail_token_path: str = "token.json"
    gmail_scopes: list = None
    
    def __post_init__(self):
        if self.gmail_scopes is None:
            self.gmail_scopes = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.modify'
            ]

@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_url: str
    db_name: str = "farm5_agents"
    connection_pool_size: int = 10
    echo_sql: bool = False

@dataclass
class AgentConfig:
    """Configuration for agent behavior"""
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    task_timeout: int = 300  # seconds
    approval_timeout: int = 3600  # seconds
    batch_size: int = 10
    rate_limit_per_minute: int = 60

@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration"""
    enable_monitoring: bool = True
    metrics_endpoint: Optional[str] = None
    alert_email: Optional[str] = None
    slack_webhook: Optional[str] = None
    log_level: str = "INFO"
    log_retention_days: int = 30

class Config:
    """Central configuration management"""
    
    def __init__(self):
        self.api = APIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4"),
            gmail_credentials_path=os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json"),
            gmail_token_path=os.getenv("GMAIL_TOKEN_PATH", "token.json")
        )
        
        self.database = DatabaseConfig(
            db_url=os.getenv("DATABASE_URL", "sqlite:///farm5_agents.db"),
            db_name=os.getenv("DB_NAME", "farm5_agents"),
            connection_pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            echo_sql=os.getenv("DB_ECHO_SQL", "false").lower() == "true"
        )
        
        self.agent = AgentConfig(
            max_retries=int(os.getenv("AGENT_MAX_RETRIES", "3")),
            retry_delay=int(os.getenv("AGENT_RETRY_DELAY", "5")),
            task_timeout=int(os.getenv("AGENT_TASK_TIMEOUT", "300")),
            approval_timeout=int(os.getenv("AGENT_APPROVAL_TIMEOUT", "3600")),
            batch_size=int(os.getenv("AGENT_BATCH_SIZE", "10")),
            rate_limit_per_minute=int(os.getenv("AGENT_RATE_LIMIT", "60"))
        )
        
        self.monitoring = MonitoringConfig(
            enable_monitoring=os.getenv("ENABLE_MONITORING", "true").lower() == "true",
            metrics_endpoint=os.getenv("METRICS_ENDPOINT"),
            alert_email=os.getenv("ALERT_EMAIL"),
            slack_webhook=os.getenv("SLACK_WEBHOOK"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_retention_days=int(os.getenv("LOG_RETENTION_DAYS", "30"))
        )
        
        # Agent-specific configurations
        self.agent_configs = self._load_agent_configs()
    
    def _load_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load agent-specific configurations from file or environment"""
        config_path = os.getenv("AGENT_CONFIG_PATH", "agent_config.json")
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configurations
        return {
            "email_manager_001": {
                "auto_reply_threshold": 0.85,
                "classification_model": "gpt-4",
                "max_emails_per_batch": 50,
                "enable_auto_responses": True
            },
            "sales_agent_001": {
                "outreach_daily_limit": 100,
                "follow_up_days": [3, 7, 14, 30],
                "lead_scoring_threshold": 70,
                "personalization_level": "high"
            },
            "research_agent_001": {
                "research_depth": "comprehensive",
                "sources_per_query": 10,
                "fact_check_enabled": True,
                "update_frequency_hours": 24
            },
            "support_agent_001": {
                "auto_assign_tickets": True,
                "priority_keywords": ["urgent", "critical", "broken", "down"],
                "response_time_sla_minutes": 60,
                "escalation_threshold": 3
            },
            "finance_agent_001": {
                "invoice_approval_required": True,
                "expense_categories": ["tools", "marketing", "operations", "personnel"],
                "budget_alert_threshold": 0.8,
                "payment_terms_days": 30
            },
            "analytics_agent_001": {
                "dashboard_refresh_minutes": 15,
                "anomaly_detection_enabled": True,
                "report_formats": ["pdf", "excel", "json"],
                "visualization_library": "plotly"
            },
            "growth_agent_001": {
                "review_frequency": "weekly",
                "optimization_threshold": 0.7,
                "strategy_planning_horizon_days": 90,
                "agent_performance_window_days": 7
            }
        }
    
    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """Get configuration for specific agent"""
        return self.agent_configs.get(agent_id, {})
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        if not self.api.openai_api_key:
            errors.append("OPENAI_API_KEY is required")
        
        if not os.path.exists(self.api.gmail_credentials_path):
            errors.append(f"Gmail credentials file not found: {self.api.gmail_credentials_path}")
        
        if self.database.db_url.startswith("sqlite://") and not os.path.exists("data"):
            os.makedirs("data", exist_ok=True)
        
        if errors:
            for error in errors:
                print(f"Configuration Error: {error}")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "api": {
                "openai_model": self.api.openai_model,
                "gmail_scopes": self.api.gmail_scopes
            },
            "database": {
                "db_url": self.database.db_url.split("://")[0] + "://***",  # Hide credentials
                "db_name": self.database.db_name,
                "connection_pool_size": self.database.connection_pool_size
            },
            "agent": {
                "max_retries": self.agent.max_retries,
                "retry_delay": self.agent.retry_delay,
                "task_timeout": self.agent.task_timeout,
                "batch_size": self.agent.batch_size,
                "rate_limit_per_minute": self.agent.rate_limit_per_minute
            },
            "monitoring": {
                "enable_monitoring": self.monitoring.enable_monitoring,
                "log_level": self.monitoring.log_level,
                "log_retention_days": self.monitoring.log_retention_days
            }
        }

# Singleton instance
config = Config()

# Example .env file content
ENV_TEMPLATE = """
# Farm 5.0 Agent System Configuration

# API Keys
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Gmail Configuration
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json

# Database
DATABASE_URL=sqlite:///data/farm5_agents.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/farm5_agents
DB_NAME=farm5_agents
DB_POOL_SIZE=10
DB_ECHO_SQL=false

# Agent Configuration
AGENT_MAX_RETRIES=3
AGENT_RETRY_DELAY=5
AGENT_TASK_TIMEOUT=300
AGENT_APPROVAL_TIMEOUT=3600
AGENT_BATCH_SIZE=10
AGENT_RATE_LIMIT=60

# Monitoring
ENABLE_MONITORING=true
METRICS_ENDPOINT=
ALERT_EMAIL=alerts@greenstem.global
SLACK_WEBHOOK=
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30

# Agent Config Path
AGENT_CONFIG_PATH=agent_config.json
"""

# Create .env template if it doesn't exist
if not os.path.exists(".env.template"):
    with open(".env.template", "w") as f:
        f.write(ENV_TEMPLATE)

# Utility functions
def get_config() -> Config:
    """Get configuration instance"""
    return config

def reload_config():
    """Reload configuration from environment"""
    global config
    config = Config()
    return config
