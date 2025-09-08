"""
Celery application for background task processing in Comms Agents.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Celery configuration
CELERY_BROKER_URL = os.getenv("RABBITMQ_URL", "amqp://comms_user:comms_password@localhost:5672/")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "comms_agents",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.scribe_tasks",
        "app.tasks.signal_tasks",
        "app.tasks.sentinel_tasks",
        "app.tasks.liaison_tasks",
        "app.tasks.conductor_tasks",
        "app.tasks.analyst_tasks",
        "app.tasks.cartographer_tasks",
        "app.tasks.workflow_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.tasks.scribe_tasks.*": {"queue": "scribe"},
        "app.tasks.signal_tasks.*": {"queue": "signal"},
        "app.tasks.sentinel_tasks.*": {"queue": "sentinel"},
        "app.tasks.liaison_tasks.*": {"queue": "liaison"},
        "app.tasks.conductor_tasks.*": {"queue": "conductor"},
        "app.tasks.analyst_tasks.*": {"queue": "analyst"},
        "app.tasks.cartographer_tasks.*": {"queue": "cartographer"},
        "app.tasks.workflow_tasks.*": {"queue": "workflows"},
    },
    
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Result backend configuration
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        # Daily morning digest
        "morning-digest": {
            "task": "app.tasks.workflow_tasks.morning_digest_workflow",
            "schedule": crontab(hour=9, minute=0),  # 9:00 AM UTC
            "args": (),
        },
        
        # Hourly signal scan
        "hourly-signal-scan": {
            "task": "app.tasks.signal_tasks.hourly_signal_scan",
            "schedule": crontab(minute=0),  # Every hour
            "args": (),
        },
        
        # Daily risk assessment
        "daily-risk-assessment": {
            "task": "app.tasks.sentinel_tasks.daily_risk_assessment",
            "schedule": crontab(hour=10, minute=0),  # 10:00 AM UTC
            "args": (),
        },
        
        # Weekly analytics report
        "weekly-analytics": {
            "task": "app.tasks.analyst_tasks.weekly_analytics_report",
            "schedule": crontab(day_of_week=1, hour=8, minute=0),  # Monday 8:00 AM UTC
            "args": (),
        },
        
        # Daily content scheduling
        "daily-content-scheduling": {
            "task": "app.tasks.conductor_tasks.daily_content_scheduling",
            "schedule": crontab(hour=7, minute=0),  # 7:00 AM UTC
            "args": (),
        },
        
        # Knowledge base update
        "knowledge-base-update": {
            "task": "app.tasks.cartographer_tasks.update_knowledge_base",
            "schedule": crontab(hour=2, minute=0),  # 2:00 AM UTC
            "args": (),
        },
    },
    
    # Task result backend
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # Security
    security_key=os.getenv("CELERY_SECURITY_KEY"),
    security_certificate=os.getenv("CELERY_SECURITY_CERTIFICATE"),
    security_cert_store=os.getenv("CELERY_SECURITY_CERT_STORE"),
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    event_queue_expires=60,
    event_queue_ttl=5,
    
    # Error handling
    task_annotations={
        "*": {
            "rate_limit": "100/m",  # 100 tasks per minute
            "time_limit": 300,      # 5 minutes
            "soft_time_limit": 240, # 4 minutes
        }
    },
    
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_remote_tracebacks=True,
    
    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
)


# Task error handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing."""
    print(f"Request: {self.request!r}")


# Health check task
@celery_app.task(bind=True)
def health_check_task(self):
    """Health check task for monitoring."""
    return {
        "status": "healthy",
        "task_id": self.request.id,
        "worker": self.request.hostname,
        "timestamp": self.request.utcnow().isoformat(),
    }


# Task monitoring
@celery_app.task(bind=True)
def monitor_task_execution(self, task_name: str, execution_time: float):
    """Monitor task execution performance."""
    # This would integrate with your monitoring system
    # For now, just log the information
    print(f"Task {task_name} completed in {execution_time:.2f} seconds")


# Task cleanup
@celery_app.task(bind=True)
def cleanup_expired_results(self):
    """Clean up expired task results."""
    # This would clean up old task results from Redis
    # Implementation depends on your specific needs
    pass


if __name__ == "__main__":
    celery_app.start()

