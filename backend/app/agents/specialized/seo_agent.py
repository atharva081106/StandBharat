from typing import Any, Dict
import json
from app.agents.base import BaseAgent
from app.agents.context import AgentContext
from app.agents.result import AgentResult
from app.agents.definition import AgentDefinition

class SEOAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="seo_agent",
            name="SEO Agent",
            description="Analyzes website structure, keywords, and identifies SEO opportunities.",
            capabilities=["seo_audit", "keyword_research", "technical_seo", "content_gaps"]
        )
        self.definition = AgentDefinition(
            id=self.agent_id,
            name=self.name,
            description=self.description,
            category="SEARCH",
            capabilities=self.capabilities,
            required_integrations=[], # GSC is optional
            input_schema={"type": "object", "properties": {"focus_area": {"type": "string"}}},
            output_schema={"type": "object"},
            approval_policy="NEVER_REQUIRE"
        )

    def execute(self, context: AgentContext) -> AgentResult:
        website_analysis = context.brand_context.get("website_analysis", {})
        
        if not website_analysis:
            return AgentResult(
                status="FAILED",
                error="No Website Analysis found. SEO Agent requires at least basic website context."
            )
            
        system_prompt = (
            "You are an expert SEO Agent. Analyze the following website structure, metadata, "
            "and content to identify technical SEO gaps, keyword opportunities, and missing schema.\n"
            "If GSC data is not provided, clearly indicate that external search performance is unavailable "
            "and base your recommendations solely on the on-page analysis.\n\n"
            "Return a JSON object containing:\n"
            "1. findings (list of strings)\n"
            "2. opportunities (list of dicts with title, impact, effort)\n"
            "3. technical_tasks (list of strings)"
        )
        
        user_message = f"Brand Context: {json.dumps(context.brand_context.get('business_overview', {}))}\n"
        user_message += f"Website Analysis: {json.dumps(website_analysis)}\n"
        
        # We don't have access to runtime.generate_with_ai here directly because execute takes context.
        # But we can import it or pass it. 
        # Actually, in the refactored AgentRuntime, it might be better if the agent gets the runtime,
        # but for now, we'll use ai_gateway directly inside execute for simplicity, or we can use it via the gateway.
        from app.ai.gateway import ai_gateway
        from app.ai.schemas import AIRequestMessage
        from app.models.all_models import AIUsageEvent
        from app.db.session import SessionLocal
        
        try:
            response = ai_gateway.generate(
                messages=[
                    AIRequestMessage(role="system", content=system_prompt),
                    AIRequestMessage(role="user", content=user_message)
                ],
                model="gpt-4o", # Assume default high-capability model
                temperature=0.3,
                max_tokens=2000
            )
            
            # Log usage manually here or let runtime do it if we refactor. Let's do it manually for now.
            db = SessionLocal()
            try:
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
            except Exception as e:
                db.rollback()
            finally:
                db.close()
                
            try:
                # Assuming the LLM returns valid JSON or markdown JSON.
                # In a robust implementation, we would use native JSON response format (e.g. response_format={"type": "json_object"})
                # We will just pass the raw content for now, or attempt to parse it.
                raw_content = response.content
                if raw_content.startswith("```json"):
                    raw_content = raw_content[7:-3]
                output_data = json.loads(raw_content)
                
                return AgentResult(status="SUCCESS", output_data=output_data)
                
            except json.JSONDecodeError:
                # Fallback if it didn't return perfect JSON
                return AgentResult(status="SUCCESS", output_data={"raw_response": response.content})
                
        except Exception as e:
            return AgentResult(status="FAILED", error=str(e))
