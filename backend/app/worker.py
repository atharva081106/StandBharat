from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.all_models import AgentRun, AgentTask, AIUsageEvent
from app.agents.registry import agent_registry
from app.agents.context import AgentContext
from app.ai.context.brand_context import brand_context_service
import uuid
import datetime

def _execute_agent_run(run_id_str: str):
    db = SessionLocal()
    try:
        run_id = uuid.UUID(run_id_str)
        run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        
        if not run:
            return
            
        run.status = "RUNNING"
        db.commit()
        
        try:
            agent = agent_registry.get_agent(run.agent_id)
            
            b_ctx = brand_context_service.get_brand_context(db, run.brand_id, run.workspace_id)
            context = AgentContext(
                run_id=run_id,
                workspace_id=run.workspace_id,
                brand_id=run.brand_id,
                user_id=uuid.UUID(int=0) if not b_ctx.brand.user_id else b_ctx.brand.user_id, # Fallback user_id if needed, or query from workspace
                input_data=run.input_context or {},
                brand_context=b_ctx
            )
            
            from app.agents.runtime import AgentRuntime
            runtime = AgentRuntime(db=db, agent=agent)
            runtime.execute_task(context)
            
        except Exception as e:
            run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
            if run:
                run.status = "FAILED"
                run.error = str(e)
                run.completed_at = datetime.datetime.utcnow()
            db.commit()
        
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3)
def execute_seo_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def execute_geo_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def execute_competitor_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def execute_growth_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def execute_content_strategy_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def execute_writer_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def execute_linkedin_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def execute_x_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def execute_reddit_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def execute_coding_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def execute_generic_agent(self, run_id_str: str):
    _execute_agent_run(run_id_str)
