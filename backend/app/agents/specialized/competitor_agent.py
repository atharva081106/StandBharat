import traceback
import json
from app.agents.base import BaseAgent
from app.agents.context import AgentContext
from app.agents.result import AgentResult
from app.ai.gateway import ai_gateway
from app.ai.schemas import AIRequestMessage
from app.ai.exceptions import AINotConfiguredException
from app.models.all_models import AIUsageEvent
from app.db.session import SessionLocal

class CompetitorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="competitor",
            name="Competitor Agent",
            description="Transforms available competitor info into structured competitive intelligence.",
            capabilities=["competitor_profile_analysis", "positioning_comparison", "competitive_gaps"]
        )

    def execute(self, context: AgentContext) -> AgentResult:
        db = SessionLocal()
        try:
            if not context.brand_context or not context.brand_context.competitors:
                return AgentResult(status="SUCCESS", output_data={
                    "status": "DATA_NOT_AVAILABLE",
                    "insights": [],
                    "summary": "No competitors defined in Brand Brain."
                })
                
            competitor_data = []
            for comp in context.brand_context.competitors:
                competitor_data.append({
                    "name": comp.name,
                    "description": comp.description,
                    "positioning": comp.positioning,
                    "strengths": comp.strengths,
                    "weaknesses": comp.weaknesses,
                    "notes": comp.notes
                })
                
            brand_info = {
                "name": context.brand_context.brand.name,
                "positioning": context.brand_context.positioning.positioning_statement if context.brand_context.positioning else "Unknown",
                "uvp": context.brand_context.positioning.unique_value_proposition if context.brand_context.positioning else "Unknown"
            }

            sys_prompt = f"""You are the Competitor Intelligence Agent for {brand_info['name']}.
Analyze the provided competitor data and our brand's positioning.
Produce a structured JSON output containing:
- "summary": Overall competitive landscape summary.
- "insights": A list of objects for each competitor containing: "competitor", "strengths", "weaknesses", "positioning_gap", "messaging_gap", "opportunities", "confidence".
Output JSON only without markdown blocks.
"""
            user_msg = f"""
Our Brand:
{json.dumps(brand_info, indent=2)}

Competitors:
{json.dumps(competitor_data, indent=2)}
"""

            messages = [
                AIRequestMessage(role="system", content=sys_prompt),
                AIRequestMessage(role="user", content=user_msg)
            ]
            
            response = ai_gateway.generate(messages=messages, max_tokens=1000)
            
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
                output_data = {"summary": response.content, "insights": []}

            return AgentResult(status="SUCCESS", output_data=output_data)

        except AINotConfiguredException as e:
            return AgentResult(status="FAILED", error=str(e))
        except Exception as e:
            return AgentResult(status="FAILED", error=f"Error: {str(e)}\n{traceback.format_exc()}")
        finally:
            db.close()
