from typing import Any, Dict, Optional
import datetime
from sqlalchemy.orm import Session
from app.models.all_models import AgentRun, AgentTask, AIUsageEvent
from app.agents.context import AgentContext
from app.agents.base import BaseAgent
from app.agents.result import AgentResult

class AgentRuntime:
    """
    Manages the lifecycle, budgeting, and execution context of an Agent.
    Responsible for telemetry, timeout limits, retries, cost logging, and state management.
    """
    def __init__(self, db: Session, agent: BaseAgent):
        self.db = db
        self.agent = agent
        
    def generate_with_ai(
        self,
        messages,
        model=None,
        temperature=0.7,
        max_tokens=2000,
        tools=None,
        context: AgentContext = None
    ):
        from app.ai.gateway import ai_gateway
        from app.models.all_models import AIUsageEvent
        
        response = ai_gateway.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools
        )
        
        if context:
            usage = AIUsageEvent(
                workspace_id=context.workspace_id,
                brand_id=context.brand_id,
                user_id=context.user_id,
                agent_id=self.agent.agent_id,
                agent_run_id=context.run_id,
                provider=response.info.provider,
                model=response.info.model,
                input_tokens=response.info.input_tokens,
                output_tokens=response.info.output_tokens,
                total_tokens=response.info.total_tokens,
                estimated_cost=response.info.estimated_cost,
                status="SUCCESS"
            )
            self.db.add(usage)
            self.db.commit()
            
        return response
        
    def execute_task(self, context: AgentContext) -> AgentResult:
        run_record = self.db.query(AgentRun).filter(AgentRun.id == context.run_id).first()
        task_record = None
        if context.task_id:
            task_record = self.db.query(AgentTask).filter(AgentTask.id == context.task_id).first()
        
        if run_record:
            run_record.started_at = datetime.datetime.utcnow()
            run_record.status = "RUNNING"
            self.db.commit()
            
        try:
            # Here we can validate required_integrations, budget, and inject tools
            result = self.agent.execute(context)
            
            if run_record:
                run_record.status = result.status
                run_record.output = result.output_data
                if result.error:
                    run_record.error = result.error
                run_record.completed_at = datetime.datetime.utcnow()
            
            if task_record:
                task_record.status = "COMPLETED" if result.status == "SUCCESS" else "FAILED"
                task_record.output_data = result.output_data
                if result.error:
                    task_record.error = result.error

            self.db.commit()
            return result
            
        except Exception as e:
            error_msg = str(e)
            if run_record:
                run_record.status = "FAILED"
                run_record.error = error_msg
                run_record.completed_at = datetime.datetime.utcnow()
            
            if task_record:
                task_record.status = "FAILED"
                task_record.error = error_msg
                
            self.db.commit()
            return AgentResult(status="FAILED", error=error_msg)
