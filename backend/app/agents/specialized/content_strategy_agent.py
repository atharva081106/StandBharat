import traceback
import json
from app.agents.base import BaseAgent
from app.agents.context import AgentContext
from app.agents.result import AgentResult
from app.ai.gateway import ai_gateway
from app.ai.schemas import AIRequestMessage
from app.ai.exceptions import AINotConfiguredException
from app.models.all_models import AIUsageEvent, AgentRun, Opportunity, ContentProject, ContentBrief
from app.db.session import SessionLocal

class ContentStrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="content_strategy",
            name="Content Strategy Agent",
            description="Transforms growth opportunities into structured content briefs.",
            capabilities=["content_brief_generation"]
        )

    def execute(self, context: AgentContext) -> AgentResult:
        db = SessionLocal()
        try:
            opportunity_id = context.input_data.get("opportunity_id")
            if not opportunity_id:
                return AgentResult(status="FAILED", error="Missing opportunity_id in input data")

            opportunity = db.query(Opportunity).filter(
                Opportunity.id == opportunity_id,
                Opportunity.brand_id == context.brand_id
            ).first()

            if not opportunity:
                return AgentResult(status="FAILED", error="Opportunity not found")

            analytics_run = db.query(AgentRun).filter(
                AgentRun.brand_id == context.brand_id, 
                AgentRun.agent_type == "analytics",
                AgentRun.status == "SUCCESS"
            ).order_by(AgentRun.completed_at.desc()).first()
            
            competitor_run = db.query(AgentRun).filter(
                AgentRun.brand_id == context.brand_id, 
                AgentRun.agent_type == "competitor",
                AgentRun.status == "SUCCESS"
            ).order_by(AgentRun.completed_at.desc()).first()

            growth_run = db.query(AgentRun).filter(
                AgentRun.brand_id == context.brand_id,
                AgentRun.agent_type == "growth",
                AgentRun.status == "SUCCESS"
            ).order_by(AgentRun.completed_at.desc()).first()

            analytics_data = analytics_run.output_data if analytics_run else "No recent analytics."
            competitor_data = competitor_run.output_data if competitor_run else "No recent competitor data."
            growth_data = growth_run.output_data if growth_run else "No recent growth data."

            sys_prompt = f"""You are the Content Strategy Agent for {context.brand_context.brand.name if context.brand_context else 'a brand'}.
Your job is to take a Growth Opportunity and turn it into a structured Content Brief.
Use the provided Brand Context, Analytics, Competitor Insights, and Growth Opportunities to ground your strategy.
Do NOT invent fake marketing evidence. Use what is provided.
Output a structured JSON object containing:
- "title": A proposed title for the content.
- "objective": The main goal of the content.
- "target_audience": The specific segment being targeted.
- "key_message": The primary takeaway.
- "angle": The unique perspective or hook.
- "content_type": One of [BLOG_POST, LINKEDIN_POST, SOCIAL_POST, EMAIL_DRAFT, LANDING_PAGE_COPY].
- "tone": The emotional register (e.g., professional, witty).
- "call_to_action": The specific action you want the reader to take.
- "keywords": A string of comma-separated keywords.
- "competitor_context": How this positions against competitors based on provided insights.
- "supporting_evidence": Data points or facts from analytics to support the message.
- "recommended_content_structure": An outline or structure for the writer.
Output JSON only without markdown blocks.
"""

            user_msg = f"""
Opportunity to address:
Title: {opportunity.title}
Description: {opportunity.description}
Impact: {opportunity.impact}

Analytics Context:
{json.dumps(analytics_data, indent=2)}

Competitor Context:
{json.dumps(competitor_data, indent=2)}

Growth Context:
{json.dumps(growth_data, indent=2)}
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
                
                # Check for existing project for this opportunity to avoid duplicates
                existing_project = db.query(ContentProject).filter(
                    ContentProject.opportunity_id == opportunity.id,
                    ContentProject.brand_id == context.brand_id
                ).first()

                if not existing_project:
                    project = ContentProject(
                        workspace_id=context.workspace_id,
                        brand_id=context.brand_id,
                        opportunity_id=opportunity.id,
                        title=output_data.get("title", f"Project for {opportunity.title}"),
                        objective=output_data.get("objective", ""),
                        content_type=output_data.get("content_type", "BLOG_POST"),
                        status="BRIEFING",
                        created_by=context.user_id
                    )
                    db.add(project)
                    db.flush()
                else:
                    project = existing_project
                    project.status = "BRIEFING"

                # Create Brief
                brief = ContentBrief(
                    content_project_id=project.id,
                    workspace_id=context.workspace_id,
                    brand_id=context.brand_id,
                    title=output_data.get("title", "Untitled Brief"),
                    objective=output_data.get("objective", ""),
                    target_audience=output_data.get("target_audience", ""),
                    key_message=output_data.get("key_message", ""),
                    angle=output_data.get("angle", ""),
                    content_type=output_data.get("content_type", "BLOG_POST"),
                    tone=output_data.get("tone", ""),
                    call_to_action=output_data.get("call_to_action", ""),
                    keywords=output_data.get("keywords", ""),
                    competitor_context=output_data.get("competitor_context", ""),
                    supporting_evidence=output_data.get("supporting_evidence", ""),
                    source_opportunity_id=opportunity.id,
                    status="DRAFT"
                )
                db.add(brief)
                db.commit()
                
                output_data["project_id"] = str(project.id)
                output_data["brief_id"] = str(brief.id)

            except Exception as e:
                db.rollback()
                output_data = {"raw_response": response.content, "parse_error": str(e)}

            return AgentResult(status="SUCCESS", output_data=output_data)

        except AINotConfiguredException as e:
            return AgentResult(status="FAILED", error=str(e))
        except Exception as e:
            return AgentResult(status="FAILED", error=f"Error: {str(e)}\n{traceback.format_exc()}")
        finally:
            db.close()
