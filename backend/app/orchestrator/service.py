from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.models.all_models import OrchestratorConfig, OrchestrationRun, AgentTask, AgentRun
from app.orchestrator.decision_engine import decision_engine
from app.agents.registry import agent_registry
from app.worker import execute_agent_task

class OrchestratorService:
    def get_config(self, db: Session, brand_id: UUID) -> OrchestratorConfig:
        config = db.query(OrchestratorConfig).filter(OrchestratorConfig.brand_id == brand_id).first()
        return config

    def update_config(self, db: Session, brand_id: UUID, workspace_id: UUID, mode: str) -> OrchestratorConfig:
        config = self.get_config(db, brand_id)
        if not config:
            config = OrchestratorConfig(
                workspace_id=workspace_id,
                brand_id=brand_id,
                mode=mode
            )
            db.add(config)
        else:
            config.mode = mode
        db.commit()
        db.refresh(config)
        return config

    def get_runs(self, db: Session, brand_id: UUID, limit: int = 50) -> List[OrchestrationRun]:
        return db.query(OrchestrationRun).filter(
            OrchestrationRun.brand_id == brand_id
        ).order_by(OrchestrationRun.created_at.desc()).limit(limit).all()

    def tick(self, db: Session, config: OrchestratorConfig):
        """
        Evaluate and potentially trigger agents for this brand based on config mode.
        """
        if config.mode == "OFF":
            return
            
        is_autonomous = config.mode == "AUTONOMOUS"

        agents_to_eval = ["analytics", "competitor", "growth", "content_strategy"]
        
        for agent_id in agents_to_eval:
            # Check if agent is already queued or running
            is_active = db.query(AgentRun).filter(
                AgentRun.brand_id == config.brand_id,
                AgentRun.agent_type == agent_id,
                AgentRun.status.in_(["RUNNING", "QUEUED"]) # QUEUED is mostly used for tasks but let's be safe
            ).first() is not None
            
            if is_active:
                continue

            # Evaluate
            decision = "SKIP"
            reason = ""
            
            if agent_id == "analytics":
                decision, reason = decision_engine.evaluate_analytics(db, config.brand_id)
            elif agent_id == "competitor":
                decision, reason = decision_engine.evaluate_competitor(db, config.brand_id)
            elif agent_id == "growth":
                decision, reason = decision_engine.evaluate_growth(db, config.brand_id)
            elif agent_id == "content_strategy":
                decision, reason, input_data = decision_engine.evaluate_content_strategy(db, config.brand_id)

            if decision == "RUN" and not is_autonomous:
                decision = "SKIP"
                reason += " (Blocked by ASSISTED mode, requires manual trigger)"
                
            # Log the decision
            run_log = OrchestrationRun(
                workspace_id=config.workspace_id,
                brand_id=config.brand_id,
                trigger_type="SCHEDULE",
                status="COMPLETED",
                decision=decision,
                agent_id=agent_id,
                reason=reason,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db.add(run_log)
            db.commit()
            
            # Enqueue if RUN
            if decision == "RUN":
                self._enqueue_agent(db, config.workspace_id, config.brand_id, agent_id, input_data if 'input_data' in locals() else {})

        config.last_run_at = datetime.utcnow()
        db.commit()

    def _enqueue_agent(self, db: Session, workspace_id: UUID, brand_id: UUID, agent_type: str, input_data: dict = None):
        task = AgentTask(
            workspace_id=workspace_id,
            brand_id=brand_id,
            agent_type=agent_type,
            task_type="analysis",
            status="QUEUED",
            input_data=input_data or {}
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        run = AgentRun(
            workspace_id=workspace_id,
            brand_id=brand_id,
            agent_type=agent_type,
            task_id=task.id,
            status="QUEUED"
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        execute_agent_task.delay(str(task.id), str(run.id))


orchestrator_service = OrchestratorService()
