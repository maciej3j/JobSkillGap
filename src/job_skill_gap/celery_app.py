from datetime import timedelta

from celery import Celery

from job_skill_gap.config import get_settings

settings = get_settings()
celery_app = Celery(
    "job_skill_gap", broker=settings.redis_url, include=["job_skill_gap.tasks"]
)
celery_app.conf.update(
    timezone="Europe/Warsaw",
    broker_connection_retry_on_startup=True,
    task_ignore_result=True,
    beat_schedule={
        "import-greenhouse": {
            "task": "job_skill_gap.tasks.import_source",
            "args": ["greenhouse"],
            "schedule": timedelta(minutes=settings.import_interval_minutes),
        },
        "import-lever": {
            "task": "job_skill_gap.tasks.import_source",
            "args": ["lever"],
            "schedule": timedelta(minutes=settings.import_interval_minutes),
        },
        "import-ashby": {
            "task": "job_skill_gap.tasks.import_source",
            "args": ["ashby"],
            "schedule": timedelta(minutes=settings.import_interval_minutes),
        },
    },
)
