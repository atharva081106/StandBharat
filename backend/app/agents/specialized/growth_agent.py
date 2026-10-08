import traceback
import json
from app.agents.base import BaseAgent
from app.agents.context import AgentContext
from app.agents.result import AgentResult
from app.ai.gateway import ai_gateway
from app.ai.schemas import AIRequestMessage
from app.ai.exceptions import AINotConfiguredException
from app.models.all_models import AIUsageEvent, AgentRun, Opportunity
from app.db.session import SessionLocal

class GrowthAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="growth",
            name="Growth Agent",
            description="Turns signals into actionable growth opportunities.",
            capabilities=["opportunity_generation"]
        )

    def execute(self, context: AgentContext) -> AgentResult:
        db = SessionLocal()
        try:
            # 1. Fetch latest Analytics and Competitor results
            analytics_run = db.query(AgentRun).filter(
                AgentRun.brand_id == context.brand_id, 
                AgentRun.agent_id == "analytics",
                AgentRun.status == "SUCCESS"
            ).order_by(AgentRun.completed_at.desc()).first()
            
            competitor_run = db.query(AgentRun).filter(
                AgentRun.brand_id == context.brand_id, 
                AgentRun.agent_id == "competitor",
                AgentRun.status == "SUCCESS"
            ).order_by(AgentRun.completed_at.desc()).first()
            
            # Fetch existing active opportunities
            existing_opps = db.query(Opportunity).filter(
                Opportunity.brand_id == context.brand_id,
                Opportunity.status.notin_(["DISMISSED", "COMPLETED"])
            ).all()

            analytics_data = analytics_run.output if analytics_run else "No recent analytics."
            competitor_data = competitor_run.output if competitor_run else "No recent competitor data."
            existing_opps_data = [{"title": o.title, "status": o.status} for o in existing_opps]

            sys_prompt = f"""You are the Growth Agent for {context.brand_context.brand.name if context.brand_context else 'a brand'}.
Review the Brand Context, Analytics Results, and Competitor Results.
Generate actionable growth opportunities. Avoid duplicating existing active opportunities.
Output a structured JSON object containing:
- "summary": A brief summary of your analysis.
- "opportunities": A list of objects containing: "title", "description", "impact" (High/Medium/Low), "confidence" (High/Medium/Low), "effort" (High/Medium/Low), "priority" (1-10), "recommended_action", "evidence".
Output JSON only without markdown blocks.
"""

            user_msg = f"""
Analytics Results:
{json.dumps(analytics_data, indent=2)}

Competitor Results:
{json.dumps(competitor_data, indent=2)}

Existing Active Opportunities:
{json.dumps(existing_opps_data, indent=2)}
"""

            messages = [
                AIRequestMessage(role="system", content=sys_prompt),
                AIRequestMessage(role="user", content=user_msg)
            ]
            
            response = ai_gateway.generate(messages=messages, max_tokens=1500)
            
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
            
            # Parse output
            try:
                raw = response.content.strip()
                if raw.startswith("```json"): raw = raw[7:]
                if raw.endswith("```"): raw = raw[:-3]
                output_data = json.loads(raw.strip())
                
                # Persist opportunities
                new_opps = []
                for opp in output_data.get("opportunities", []):
                    new_opp = Opportunity(
                        workspace_id=context.workspace_id,
                        brand_id=context.brand_id,
                        title=opp.get("title", "Untitled Opportunity"),
                        description=f"{opp.get('description', '')}\nAction: {opp.get('recommended_action', '')}\nEvidence: {opp.get('evidence', '')}",
                        impact=opp.get("impact", "Medium"),
                        confidence=opp.get("confidence", "Medium"),
                        effort=opp.get("effort", "Medium"),
                        priority=opp.get("priority", 5),
                        status="NEW",
                        source="AGENT_GENERATED"
                    )
                    db.add(new_opp)
                    new_opps.append(new_opp)
                
                db.commit()
                
            except Exception as e:
                db.rollback()
                output_data = {"summary": response.content, "opportunities": [], "parse_error": str(e)}

            return AgentResult(status="SUCCESS", output_data=output_data)

        except AINotConfiguredException as e:
            return AgentResult(status="FAILED", error=str(e))
        except Exception as e:
            return AgentResult(status="FAILED", error=f"Error: {str(e)}\n{traceback.format_exc()}")
        finally:
            db.close()
