from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.all_models import AgentRun, AgentTask, AIUsageEvent
from app.agents.registry import agent_registry
from app.agents.context import AgentContext
from app.ai.context.brand_context import brand_context_service
import uuid
import datetime

@celery_app.task(bind=True, max_retries=3)
def execute_agent_task(self, task_id_str: str, run_id_str: str):
    db = SessionLocal()
    try:
        task_id = uuid.UUID(task_id_str)
        run_id = uuid.UUID(run_id_str)
        
        run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        task = db.query(AgentTask).filter(AgentTask.id == task_id).first()
        
        if not run or not task:
            return
            
        run.status = "RUNNING"
        db.commit()
        
        try:
            agent = agent_registry.get_agent(task.agent_type)
            
            b_ctx = brand_context_service.get_brand_context(db, task.brand_id, task.workspace_id)
            context = AgentContext(
                task_id=task_id,
                run_id=run_id,
                workspace_id=task.workspace_id,
                brand_id=task.brand_id,
                user_id=task.created_by,
                input_data=task.input_data or {},
                brand_context=b_ctx
            )
            
            result = agent.execute(context)
            
            run.status = result.status
            run.output_data = result.output_data
            if result.error:
                run.error = result.error
                
            task.status = "COMPLETED" if result.status == "SUCCESS" else "FAILED"
            
        except Exception as e:
            run.status = "FAILED"
            run.error = str(e)
            task.status = "FAILED"
            
        run.completed_at = datetime.datetime.utcnow()
        db.commit()
        
    finally:
        db.close()
