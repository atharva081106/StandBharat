import traceback
import json
from app.agents.base import BaseAgent
from app.agents.definition import AgentDefinition
from app.agents.context import AgentContext
from app.agents.result import AgentResult
from app.ai.gateway import ai_gateway
from app.ai.schemas import AIRequestMessage
from app.ai.exceptions import AINotConfiguredException
from app.models.all_models import AIUsageEvent, ContentDraft, ContentVersion
from app.db.session import SessionLocal

class XAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="x_agent",
            name="X Agent",
            description="Manages X (Twitter) publishing and performance.",
            capabilities=["draft", "publish", "metrics"]
        )
        self.definition = AgentDefinition(
            id="x_agent",
            name="X Agent",
            description="Manages X (Twitter) publishing and performance.",
            category="CHANNEL",
            capabilities=["draft", "publish", "metrics"],
            required_integrations=["X"],
            input_schema={"type": "object", "properties": {"topic": {"type": "string"}}},
            output_schema={"type": "object"},
            approval_policy="ALWAYS_REQUIRE"
        )

    def execute(self, context: AgentContext) -> AgentResult:
        db = SessionLocal()
        try:
            from app.integrations.registry import integration_registry
            provider = integration_registry.get_provider("twitter_x")
            is_connected = provider.validate(context.workspace_id)
            
            topic = context.input_data.get("topic", "General Brand Update")
            
            sys_prompt = f"""You are an expert Twitter/X Social Media Manager for {context.brand_context.brand.name if context.brand_context and context.brand_context.get('brand') else 'a brand'}.
Your job is to generate a high-quality Twitter/X post draft based on the provided Topic and Brand Context.
Adhere strictly to the brand voice, tone, positioning, and rules. Ensure it is under 280 characters.
Output a structured JSON object containing:
- "title": The title of the draft (internal reference).
- "body": The main content for the X post (use emojis and hashtags appropriately).
- "metadata": Any useful generation notes or alternative suggestions.
Output JSON only without markdown blocks.
"""
            
            brand_voice = ""
            if context.brand_context and "brand_voice" in context.brand_context:
                bv = context.brand_context.get("brand_voice", {})
                brand_voice = f"Tone: {bv.get('tone')}\nStyle: {bv.get('writing_style')}\nRules: {bv.get('messaging_rules')}"

            user_msg = f"""
Brand Voice & Rules:
{brand_voice}

Topic: {topic}

Generate the X post draft.
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
                
                # Create Draft
                draft = ContentDraft(
                    workspace_id=context.workspace_id,
                    brand_id=context.brand_id,
                    content_type="X_POST",
                    title=output_data.get("title", "X Draft"),
                    body=output_data.get("body", ""),
                    status="DRAFT",
                    generated_by="x_agent",
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
                    change_summary="Initial X AI Draft",
                    created_by="x_agent"
                )
                db.add(version)

                db.commit()
                
                output_data["draft_id"] = str(draft.id)
                output_data["version_id"] = str(version.id)
                if not is_connected:
                    output_data["warning"] = "X integration is disconnected. Draft was created, but external publishing is unavailable."

            except Exception as e:
                db.rollback()
                output_data = {"raw_response": response.content, "parse_error": str(e)}
                return AgentResult(status="FAILED", error=str(e))

            status = "SUCCESS_WITH_WARNINGS" if not is_connected else "SUCCESS"
            return AgentResult(status=status, output_data=output_data)

        except AINotConfiguredException as e:
            return AgentResult(status="FAILED", error=str(e))
        except Exception as e:
            return AgentResult(status="FAILED", error=f"Error: {str(e)}\n{traceback.format_exc()}")
        finally:
            db.close()
