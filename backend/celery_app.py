from celery import Celery
from celery.schedules import crontab
import os

# Redis URL for Celery broker and backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "pc_price_tracker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "backend.tasks.scraping_task",
        "backend.tasks.search_task",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Beat schedule - daily scraping tasks
    beat_schedule={
        # URL-based scraping at 11:59 PM UTC
        "scrape-all-products-daily": {
            "task": "backend.tasks.scraping_task.scrape_all_products",
            "schedule": crontab(hour=23, minute=59),
            "options": {"queue": "scraping"}
        },
        # Search-based scraping at 6:00 AM UTC (2:00 PM Manila time)
        "scrape-search-configs-daily": {
            "task": "backend.tasks.search_task.scrape_all_search_configs",
            "schedule": crontab(hour=6, minute=0),
            "options": {"queue": "scraping"}
        },
    },
    
    # Task routes
    task_routes={
        "backend.tasks.scraping_task.*": {"queue": "scraping"},
        "backend.tasks.search_task.*": {"queue": "scraping"},
    },
)

# Optional: Configure task time limits
# Search tasks can take longer due to pagination
celery_app.conf.task_time_limit = 7200  # 2 hours max per task
celery_app.conf.task_soft_time_limit = 6600  # Soft limit at 110 minutes
