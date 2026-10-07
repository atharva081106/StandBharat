from celery import Celery
import os

# fallback for sqlite test
broker_url = os.environ.get("REDIS_URL", "sqla+sqlite:///celery_broker.db")
result_backend = os.environ.get("REDIS_URL", "db+sqlite:///celery_results.db")

celery_app = Celery(
    "standbharat_worker",
    broker=broker_url,
    backend=result_backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task
def dummy_agent_task(task_id: str):
    print(f"Executing agent task {task_id}")
    return {"status": "success", "task_id": task_id}
