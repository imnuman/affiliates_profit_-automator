"""
Celery application configuration
"""
from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery app
celery_app = Celery(
    "clickbank_saas",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.content",
        "app.tasks.sync",
        "app.tasks.publishing",
        "app.tasks.analytics",
        "app.tasks.scheduled"
    ]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "sync-clickbank-products-hourly": {
        "task": "app.tasks.sync.sync_clickbank_products",
        "schedule": crontab(minute=0),  # Every hour
    },
    "sync-user-sales-hourly": {
        "task": "app.tasks.sync.sync_user_sales",
        "schedule": crontab(minute=15),  # Every hour at :15
    },
    "process-scheduled-content": {
        "task": "app.tasks.publishing.process_scheduled_content",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "send-scheduled-emails": {
        "task": "app.tasks.publishing.send_scheduled_emails",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "generate-daily-insights": {
        "task": "app.tasks.analytics.generate_daily_insights",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    "send-performance-summaries": {
        "task": "app.tasks.scheduled.send_performance_summaries",
        "schedule": crontab(hour=8, minute=0),  # Daily at 8 AM
    },
    "cleanup-old-cache": {
        "task": "app.tasks.scheduled.cleanup_old_cache",
        "schedule": crontab(hour=4, minute=0),  # Daily at 4 AM
    },
}

if __name__ == "__main__":
    celery_app.start()
