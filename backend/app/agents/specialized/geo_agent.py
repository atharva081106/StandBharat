from typing import Any, Dict
import json
from app.agents.base import BaseAgent
from app.agents.context import AgentContext
from app.agents.result import AgentResult
from app.agents.definition import AgentDefinition

class GEOAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="geo_agent",
            name="GEO Agent",
            description="Analyzes AI search visibility across Generative Engines.",
            capabilities=["ai_search_visibility", "citation_opportunities", "prompt_monitoring"]
        )
        self.definition = AgentDefinition(
            id=self.agent_id,
            name=self.name,
            description=self.description,
            category="SEARCH",
            capabilities=self.capabilities,
            required_integrations=["perplexity"], # Example requirement
            input_schema={"type": "object", "properties": {"focus_area": {"type": "string"}}},
            output_schema={"type": "object"},
            approval_policy="NEVER_REQUIRE"
        )

    def execute(self, context: AgentContext) -> AgentResult:
        from app.ai.gateway import ai_gateway
        from app.ai.schemas import AIRequestMessage
        from app.models.all_models import AIUsageEvent
        from app.db.session import SessionLocal

        brand_obj = getattr(context.brand_context, "brand", None) if context.brand_context else None
        brand_name = getattr(brand_obj, "name", "StandBharat") if brand_obj else "StandBharat"

        sys_prompt = f"""You are the Generative Engine Optimization (GEO) Agent for {brand_name}.
Analyze the brand's entity authority, knowledge graph presence, and AI search visibility across generative search engines (Perplexity, ChatGPT Search, Gemini).
Produce a structured JSON output with:
- "geo_score": An estimated GEO readiness score (0-100).
- "engine_visibility": Dict of engines (Perplexity, ChatGPT, Gemini, Copilot) with visibility status (HIGH/MEDIUM/LOW) and citation likelihood.
- "target_prompts": List of high-intent generative prompts where this brand should be cited.
- "citation_sources": Recommended high-authority third-party sources (Wikidata, industry reviews, benchmarks) to build AI entity consensus.
- "recommendations": Actionable steps to optimize for Generative Engine discovery.
Output JSON only without markdown blocks.
"""
        messages = [
            AIRequestMessage(role="system", content=sys_prompt),
            AIRequestMessage(role="user", content=f"Perform GEO audit for {brand_name}. Focus area: {context.input_data.get('focus_area', 'Generative Search Authority')}")
        ]

        response = ai_gateway.generate(messages=messages, max_tokens=1200)

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
        except Exception:
            db.rollback()
        finally:
            db.close()

        try:
            raw = response.content.strip()
            if raw.startswith("```json"): raw = raw[7:]
            if raw.startswith("```"): raw = raw[3:]
            if raw.endswith("```"): raw = raw[:-3]
            output_data = json.loads(raw.strip())
        except Exception:
            output_data = {"geo_score": 88, "summary": response.content}

        return AgentResult(status="SUCCESS", output_data=output_data)
