import traceback
import json
from app.agents.base import BaseAgent
from app.agents.context import AgentContext
from app.agents.result import AgentResult
from app.ai.gateway import ai_gateway
from app.ai.schemas import AIRequestMessage
from app.ai.exceptions import AINotConfiguredException
from app.models.all_models import AIUsageEvent, MetricSnapshot, ActivityEvent, Opportunity
from app.db.session import SessionLocal

class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="analytics",
            name="Analytics Agent",
            description="Analyzes marketing/business performance data.",
            capabilities=["performance_summary", "trend_detection", "opportunity_signals"]
        )

    def execute(self, context: AgentContext) -> AgentResult:
        db = SessionLocal()
        try:
            # 1. Fetch available data deterministically
            metrics = db.query(MetricSnapshot).filter(MetricSnapshot.brand_id == context.brand_id).order_by(MetricSnapshot.recorded_at.desc()).limit(20).all()
            activities = db.query(ActivityEvent).filter(ActivityEvent.brand_id == context.brand_id).order_by(ActivityEvent.created_at.desc()).limit(20).all()
            
            if not metrics and not activities:
                return AgentResult(status="SUCCESS", output_data={
                    "summary": "No data available yet.",
                    "signals": [],
                    "recommendations": [],
                    "status": "DATA_NOT_AVAILABLE"
                })

            metric_summaries = [{"metric": m.metric_name, "value": m.value, "date": str(m.recorded_at)} for m in metrics]
            activity_summaries = [{"type": a.type, "description": a.description, "date": str(a.created_at)} for a in activities]

            data_context = f"""
Available Metrics:
{json.dumps(metric_summaries, indent=2)}

Recent Activity:
{json.dumps(activity_summaries, indent=2)}
"""
            sys_prompt = f"""You are the Analytics Agent for a brand.
Review the provided data and produce a structured JSON output with the following keys:
- "summary": A brief interpretation of the performance.
- "signals": A list of objects with "metric", "direction" (UP/DOWN/FLAT), "magnitude", "confidence".
- "recommendations": A list of short actionable recommendations.

Brand Context:
{context.brand_context.brand.name if context.brand_context else "Unknown Brand"}

Output JSON only without markdown blocks.
"""

            messages = [
                AIRequestMessage(role="system", content=sys_prompt),
                AIRequestMessage(role="user", content=data_context)
            ]
            
            response = ai_gateway.generate(messages=messages, max_tokens=800)
            
            # Log usage
            usage = AIUsageEvent(
                workspace_id=context.workspace_id,
                brand_id=context.brand_id,
                user_id=context.user_id,
                agent_id=self.agent_id,
                agent_run_id=context.run_id,
                provider=response.info.provider,
                model=response.info.model,
                input_tokens=response.info.input_tokens,
                output_tokens=response.info.output_tokens,
                total_tokens=response.info.total_tokens,
                estimated_cost=response.info.estimated_cost,
                status="SUCCESS"
            )
            db.add(usage)
            db.commit()
            
            # Parse output
            try:
                raw = response.content.strip()
                if raw.startswith("```json"): raw = raw[7:]
                if raw.endswith("```"): raw = raw[:-3]
                output_data = json.loads(raw.strip())
            except:
                output_data = {"summary": response.content, "signals": [], "recommendations": []}

            return AgentResult(status="SUCCESS", output_data=output_data)

        except AINotConfiguredException as e:
            return AgentResult(status="FAILED", error=str(e))
        except Exception as e:
            return AgentResult(status="FAILED", error=f"Error: {str(e)}\n{traceback.format_exc()}")
        finally:
            db.close()
