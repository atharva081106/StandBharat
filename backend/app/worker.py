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

@celery_app.task(bind=True, max_retries=3)
def execute_agent_task(self, task_id_str: str, run_id_str: str):
    _execute_agent_run(run_id_str)

@celery_app.task(bind=True, max_retries=3)
def sync_integration(self, sync_run_id_str: str):
    db = SessionLocal()
    from app.models.all_models import IntegrationSyncRun, Integration
    from app.integrations.registry import integration_registry
    try:
        sync_run_id = uuid.UUID(sync_run_id_str)
        run = db.query(IntegrationSyncRun).filter(IntegrationSyncRun.id == sync_run_id).first()
        if not run:
            return
            
        # Avoid concurrent duplicate syncs for the same integration
        concurrent_running = db.query(IntegrationSyncRun).filter(
            IntegrationSyncRun.integration_id == run.integration_id,
            IntegrationSyncRun.status == "RUNNING",
            IntegrationSyncRun.id != run.id
        ).first()
        if concurrent_running:
            run.status = "SKIPPED"
            run.error = "Another sync is currently in progress for this integration"
            run.completed_at = datetime.datetime.utcnow()
            db.commit()
            return

        run.status = "RUNNING"
        run.started_at = datetime.datetime.utcnow()
        db.commit()
        
        integration = db.query(Integration).filter(Integration.id == run.integration_id).first()
        if not integration:
            run.status = "FAILED"
            run.error = "Integration not found"
            run.completed_at = datetime.datetime.utcnow()
            db.commit()
            return
            
        try:
            provider = integration_registry.get_provider(integration.provider)
            # Pass exact workspace, brand, and integration IDs for multi-brand tenant isolation
            result = provider.sync(
                workspace_id=str(run.workspace_id),
                brand_id=str(run.brand_id) if run.brand_id else (str(integration.brand_id) if integration.brand_id else None),
                integration_id=str(integration.id)
            )
            
            if result.get("status") == "rate_limited":
                run.status = "RETRYING"
                run.error = result.get("error")
                db.commit()
                if self.request.retries < self.max_retries:
                    self.retry(countdown=300, exc=Exception(result.get("error")))
                else:
                    run.status = "FAILED"
                    integration.last_error = f"Rate limit retry limit exceeded: {result.get('error')}"
                    db.commit()
                return

            if result.get("status") == "failed":
                run.status = "FAILED"
                run.error = result.get("error")
                integration.status = "ERROR"
                integration.last_error = result.get("error")
            else:
                run.status = "COMPLETED"
                run.records_processed = result.get("records_processed", result.get("metrics_synced", 0))
                integration.last_sync_at = datetime.datetime.utcnow()
                integration.status = "CONNECTED"
                integration.last_error = None
        except Exception as e:
            run.status = "FAILED"
            run.error = str(e)
            integration.status = "ERROR"
            integration.last_error = str(e)
            
        run.completed_at = datetime.datetime.utcnow()
        db.commit()
    except Exception as e:
        # Catch all for unexpected errors
        pass
    finally:
        db.close()

@celery_app.task
def sync_all_active_integrations():
    """
    Periodic Celery Beat task that iterates over connected GA4 and GSC integrations
    and dispatches incremental synchronization, avoiding duplicates and honoring rate limits.
    """
    db = SessionLocal()
    from app.models.all_models import Integration, IntegrationSyncRun
    try:
        active_integrations = db.query(Integration).filter(
            Integration.status == "CONNECTED",
            Integration.provider.in_(["ga4", "gsc"])
        ).all()
        
        dispatched_count = 0
        now = datetime.datetime.utcnow()
        for integ in active_integrations:
            # 1. Skip if another run is queued or running
            active_run = db.query(IntegrationSyncRun).filter(
                IntegrationSyncRun.integration_id == integ.id,
                IntegrationSyncRun.status.in_(["QUEUED", "RUNNING"])
            ).first()
            if active_run:
                continue

            # 2. Skip if synced within the last 4 hours
            if integ.last_sync_at and (now - integ.last_sync_at).total_seconds() < 14400:
                continue

            # 3. Create Queued Sync Run
            new_run = IntegrationSyncRun(
                integration_id=integ.id,
                workspace_id=integ.workspace_id,
                brand_id=integ.brand_id,
                provider_id=integ.provider,
                status="QUEUED"
            )
            db.add(new_run)
            db.commit()
            
            try:
                sync_integration.delay(str(new_run.id))
                dispatched_count += 1
            except Exception as dispatch_err:
                new_run.status = "FAILED"
                new_run.error = f"Dispatch failed: {str(dispatch_err)}"
                db.commit()

        return {"dispatched": dispatched_count}
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=1)
def analyze_performance_loop(self, workspace_id_str: str, brand_id_str: str):
    """
    Scheduled learning pipeline that runs performance analysis
    and generates Next Best Actions (Opportunities).
    """
    db = SessionLocal()
    try:
        from app.models.all_models import Brand
        from app.agents.specialized.performance_agent import PerformanceAgent
        from app.agents.specialized.growth_agent import GrowthAgent
        from app.agents.context import AgentContext
        
        workspace_id = uuid.UUID(workspace_id_str)
        brand_id = uuid.UUID(brand_id_str)
        
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            return "Brand not found"
            
        # Create a mock AgentRun for the scheduled loop
        run_id = uuid.uuid4()
        
        context = AgentContext(
            run_id=run_id,
            workspace_id=workspace_id,
            brand_id=brand_id,
            user_id=uuid.UUID(int=0), # System task
            input_data={"trigger": "scheduled_learning_pipeline"}
        )
        
        # 1. Run Performance Agent to analyze metrics and create granular opportunities
        perf_agent = PerformanceAgent()
        perf_result = perf_agent.execute(context)
        
        # 2. Run Growth Agent to look at high-level business goals
        growth_agent = GrowthAgent()
        growth_result = growth_agent.execute(context)
        
        return {
            "status": "COMPLETED",
            "performance_result": perf_result.status,
            "growth_result": growth_result.status
        }
        
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}
    finally:
        db.close()
