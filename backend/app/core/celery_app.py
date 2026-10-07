from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.task_routes = {}
if settings.REDIS_URL.endswith("test"):
    celery_app.conf.task_always_eager = True

# For pytest we can also check if we are in testing:
import sys
if "pytest" in sys.modules:
    celery_app.conf.task_always_eager = True

from celery.schedules import crontab
celery_app.conf.beat_schedule = {
    'orchestrator-tick-every-15-minutes': {
        'task': 'orchestrator_tick',
        'schedule': crontab(minute='*/15'),
    },
}

# Auto-discover tasks in our orchestrator module
celery_app.autodiscover_tasks(["app.orchestrator.scheduler", "app.worker", "app.publishing"])
