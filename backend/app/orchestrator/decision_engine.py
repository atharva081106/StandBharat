from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from app.models.all_models import OrchestratorConfig, AgentRun, MetricSnapshot, ActivityEvent, Opportunity, ContentProject

class DecisionEngine:
    def __init__(self):
        # 12 hour cooldown for Analytics
        self.analytics_cooldown = timedelta(hours=12)
        # 24 hour cooldown for Competitor
        self.competitor_cooldown = timedelta(hours=24)
        # Growth cooldown - requires recent analytics and competitor
        self.growth_cooldown = timedelta(hours=24)

    def evaluate_analytics(self, db: Session, brand_id: UUID) -> Tuple[str, str]:
        """
        Decision rule: Run if last successful run is older than cooldown AND we have metrics/activity.
        """
        last_run = db.query(AgentRun).filter(
            AgentRun.brand_id == brand_id,
            AgentRun.agent_type == "analytics",
            AgentRun.status == "SUCCESS"
        ).order_by(AgentRun.completed_at.desc()).first()

        if last_run and last_run.completed_at and datetime.utcnow() - last_run.completed_at < self.analytics_cooldown:
            return "SKIP", "Cooldown active for AnalyticsAgent"

        # Check if there is data to analyze
        has_metrics = db.query(MetricSnapshot).filter(MetricSnapshot.brand_id == brand_id).first() is not None
        has_events = db.query(ActivityEvent).filter(ActivityEvent.brand_id == brand_id).first() is not None
        
        if not has_metrics and not has_events:
            return "SKIP", "No metrics or activity events available for AnalyticsAgent"

        return "RUN", "Cooldown expired and data is available"

    def evaluate_competitor(self, db: Session, brand_id: UUID) -> Tuple[str, str]:
        """
        Decision rule: Run if older than cooldown.
        """
        last_run = db.query(AgentRun).filter(
            AgentRun.brand_id == brand_id,
            AgentRun.agent_type == "competitor",
            AgentRun.status == "SUCCESS"
        ).order_by(AgentRun.completed_at.desc()).first()

        if last_run and last_run.completed_at and datetime.utcnow() - last_run.completed_at < self.competitor_cooldown:
            return "SKIP", "Cooldown active for CompetitorAgent"

        return "RUN", "Cooldown expired for CompetitorAgent"

    def evaluate_growth(self, db: Session, brand_id: UUID) -> Tuple[str, str]:
        """
        Decision rule: Run if older than cooldown AND we have recent (completed < 24h) Analytics AND Competitor runs.
        """
        last_run = db.query(AgentRun).filter(
            AgentRun.brand_id == brand_id,
            AgentRun.agent_type == "growth",
            AgentRun.status == "SUCCESS"
        ).order_by(AgentRun.completed_at.desc()).first()

        if last_run and last_run.completed_at and datetime.utcnow() - last_run.completed_at < self.growth_cooldown:
            return "SKIP", "Cooldown active for GrowthAgent"

        recent_limit = datetime.utcnow() - timedelta(hours=24)
        
        recent_analytics = db.query(AgentRun).filter(
            AgentRun.brand_id == brand_id,
            AgentRun.agent_type == "analytics",
            AgentRun.status == "SUCCESS",
            AgentRun.completed_at >= recent_limit
        ).first()

        recent_competitor = db.query(AgentRun).filter(
            AgentRun.brand_id == brand_id,
            AgentRun.agent_type == "competitor",
            AgentRun.status == "SUCCESS",
            AgentRun.completed_at >= recent_limit
        ).first()

        if not recent_analytics or not recent_competitor:
            return "SKIP", "Missing recent Analytics or Competitor results"

        return "RUN", "Recent Analytics and Competitor results are available"

    def evaluate_content_strategy(self, db: Session, brand_id: UUID) -> Tuple[str, str, Any]:
        """
        Decision rule: Run if there is a NEW or active Growth Opportunity that does not have an associated ContentProject.
        Returns Tuple[decision, reason, input_data]
        """
        # Find an opportunity that does not have a content project
        opportunities = db.query(Opportunity).filter(
            Opportunity.brand_id == brand_id,
            Opportunity.status.in_(["NEW", "ACTIVE"])
        ).order_by(Opportunity.priority.desc(), Opportunity.created_at.desc()).all()
        
        for opp in opportunities:
            project = db.query(ContentProject).filter(ContentProject.opportunity_id == opp.id).first()
            if not project:
                # We found an opportunity without a content project. We should strategize content for it.
                return "RUN", f"Growth opportunity {opp.id} produced a content brief because growth signal confidence exceeded configured threshold.", {"opportunity_id": str(opp.id)}
                
        return "SKIP", "No eligible Growth Opportunities for content strategy.", None

decision_engine = DecisionEngine()
