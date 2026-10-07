from sqlalchemy.orm import Session
from uuid import UUID
from app.models.all_models import AgentRun

class AgentResultService:
    def get_latest_agent_results(self, db: Session, brand_id: UUID) -> dict:
        results = {}
        for agent_type in ["analytics", "competitor", "growth"]:
            run = db.query(AgentRun).filter(
                AgentRun.brand_id == brand_id,
                AgentRun.agent_type == agent_type,
                AgentRun.status == "SUCCESS"
            ).order_by(AgentRun.completed_at.desc()).first()
            if run:
                results[agent_type] = run.output_data
        return results

agent_result_service = AgentResultService()
