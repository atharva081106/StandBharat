import traceback
import json
from app.agents.base import BaseAgent
from app.agents.context import AgentContext
from app.agents.result import AgentResult
from app.ai.gateway import ai_gateway
from app.ai.schemas import AIRequestMessage
from app.ai.exceptions import AINotConfiguredException
from app.models.all_models import AIUsageEvent, AgentRun, ContentBrief, ContentDraft, ContentVersion, ContentProject
from app.db.session import SessionLocal

class ContentWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="content_writer",
            name="Content Writer Agent",
            description="Generates content drafts based on content briefs and brand context.",
            capabilities=["content_draft_generation"]
        )
        from app.agents.definition import AgentDefinition
        self.definition = AgentDefinition(
            id=self.agent_id,
            name=self.name,
            description=self.description,
            category="CONTENT",
            capabilities=self.capabilities,
            required_integrations=[],
            input_schema={"type": "object", "properties": {"brief_id": {"type": "string"}}},
            output_schema={"type": "object"},
            approval_policy="DEFAULT"
        )

    def execute(self, context: AgentContext) -> AgentResult:
        db = SessionLocal()
        try:
            brief_id = context.input_data.get("brief_id")
            if not brief_id:
                return AgentResult(status="FAILED", error="Missing brief_id in input data")

            brief = db.query(ContentBrief).filter(
                ContentBrief.id == brief_id,
                ContentBrief.brand_id == context.brand_id
            ).first()

            if not brief:
                return AgentResult(status="FAILED", error="Content brief not found")

            project = db.query(ContentProject).filter(
                ContentProject.id == brief.content_project_id
            ).first()

            sys_prompt = f"""You are an expert Content Writer for {context.brand_context.brand.name if context.brand_context else 'a brand'}.
Your job is to generate a high-quality content draft based on the provided Content Brief and Brand Context.
Adhere strictly to the brand voice, tone, positioning, and rules.
Do not invent facts or claims not supported by the brief or brand context.
Ensure the content type ({brief.content_type}) dictates the format.
Output a structured JSON object containing:
- "title": The title of the draft.
- "body": The main content generated (use markdown if appropriate for the content type).
- "metadata": Any useful generation notes or alternative suggestions.
Output JSON only without markdown blocks.
"""

            brand_voice = ""
            if "brand_voice" in context.brand_context:
                bv = context.brand_context.get("brand_voice", {})
                brand_voice = f"Tone: {bv.get('tone')}\nStyle: {bv.get('writing_style')}\nRules: {bv.get('messaging_rules')}"

            strategy = ""
            if "strategy" in context.brand_context:
                strategy = json.dumps(context.brand_context["strategy"], indent=2)

            user_msg = f"""
Brand Voice & Rules:
{brand_voice}

Strategy Documents (Content/Marketing strategy, Positioning, etc):
{strategy}

Content Brief:
Title: {brief.title}
Objective: {brief.objective}
Target Audience: {brief.target_audience}
Key Message: {brief.key_message}
Angle: {brief.angle}
Tone: {brief.tone}
Call to Action: {brief.call_to_action}
Keywords: {brief.keywords}
Competitor Context: {brief.competitor_context}
Supporting Evidence: {brief.supporting_evidence}

Generate the draft.
"""

            messages = [
                AIRequestMessage(role="system", content=sys_prompt),
                AIRequestMessage(role="user", content=user_msg)
            ]
            
            response = ai_gateway.generate(messages=messages, max_tokens=2500)
            
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
                
                # Create Draft
                draft = ContentDraft(
                    content_project_id=brief.content_project_id,
                    brief_id=brief.id,
                    workspace_id=context.workspace_id,
                    brand_id=context.brand_id,
                    content_type=brief.content_type,
                    title=output_data.get("title", "Draft"),
                    body=output_data.get("body", ""),
                    status="DRAFT",
                    generated_by="content_writer_agent",
                    generation_metadata=output_data.get("metadata", {})
                )
                db.add(draft)
                db.flush()

                # Create first version
                version = ContentVersion(
                    content_draft_id=draft.id,
                    version_number=1,
                    title=draft.title,
                    body=draft.body,
                    change_summary="Initial AI Draft",
                    created_by="content_writer_agent"
                )
                db.add(version)

                if project:
                    project.status = "DRAFTING"

                db.commit()
                
                output_data["draft_id"] = str(draft.id)
                output_data["version_id"] = str(version.id)

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
