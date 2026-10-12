from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_routes={},
    include=[
        "app.orchestrator.scheduler",
        "app.worker",
        "app.publishing.tasks",
        "app.workers.celery_worker"
    ],
    # Redis Hardening & Reliability Configurations
    broker_connection_retry_on_startup=True,
    broker_pool_limit=10,
    broker_connection_max_retries=10,
    broker_connection_timeout=30.0,
    redis_socket_keepalive=True,
    redis_socket_timeout=30.0,
    redis_retry_on_timeout=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
)
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
    'sync-active-integrations-every-6-hours': {
        'task': 'app.worker.sync_all_active_integrations',
        'schedule': crontab(minute='0', hour='*/6'),
    },
    'recover-stale-publications-every-30-minutes': {
        'task': 'recover_stale_publications',
        'schedule': crontab(minute='*/30'),
    },
}

# Auto-discover tasks in our modules
celery_app.autodiscover_tasks(["app.orchestrator.scheduler", "app.worker", "app.publishing", "app.workers.celery_worker"])
