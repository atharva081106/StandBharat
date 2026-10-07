from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.all_models import OrchestratorConfig
from app.orchestrator.service import orchestrator_service

@celery_app.task(name="orchestrator_tick")
def orchestrator_tick_task():
    """
    Periodic task to evaluate and schedule autonomous agent workflows.
    """
    db = SessionLocal()
    try:
        # Load all enabled configurations
        configs = db.query(OrchestratorConfig).filter(
            OrchestratorConfig.mode.in_(["AUTONOMOUS", "ASSISTED"])
        ).all()

        for config in configs:
            try:
                orchestrator_service.tick(db, config)
            except Exception as e:
                # Log and continue to next brand
                db.rollback()
                print(f"Error ticking orchestrator for brand {config.brand_id}: {e}")
                
    finally:
        db.close()
