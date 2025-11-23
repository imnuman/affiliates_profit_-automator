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
        "app.tasks.content_tasks",
        "app.tasks.clickbank_tasks",
        "app.tasks.publishing_tasks",
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
    "sync-clickbank-products-daily": {
        "task": "app.tasks.clickbank_tasks.sync_clickbank_products",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    "update-product-metrics-hourly": {
        "task": "app.tasks.clickbank_tasks.update_product_metrics",
        "schedule": crontab(minute=30),  # Every hour at :30
    },
    "identify-trending-products-daily": {
        "task": "app.tasks.clickbank_tasks.identify_trending_products",
        "schedule": crontab(hour=6, minute=0),  # Daily at 6 AM
    },
    "publish-scheduled-content": {
        "task": "app.tasks.publishing_tasks.publish_scheduled_content",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "cleanup-stale-products-weekly": {
        "task": "app.tasks.clickbank_tasks.cleanup_stale_products",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday at 3 AM
    },
}

if __name__ == "__main__":
    celery_app.start()
