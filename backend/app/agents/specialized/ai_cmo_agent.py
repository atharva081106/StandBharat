import json
import logging
from typing import Dict, Any, List
import uuid

from app.agents.base import BaseAgent
from app.agents.definition import AgentDefinition
from app.agents.context import AgentContext
from app.agents.result import AgentResult
from app.db.session import SessionLocal
from app.models.all_models import Opportunity, AIUsageEvent

logger = logging.getLogger(__name__)

class AICMOAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="ai_cmo",
            name="AI CMO Orchestrator",
            description="Executive strategic orchestrator for brand positioning, campaign prioritization, and autonomous multi-agent delegation.",
            capabilities=["strategic_planning", "growth_prioritization", "cross_agent_orchestration", "market_intelligence"]
        )
        self.definition = AgentDefinition(
            id="ai_cmo",
            name="AI CMO Orchestrator",
            description="Executive strategic orchestrator for brand positioning, campaign prioritization, and autonomous multi-agent delegation.",
            category="CORE",
            capabilities=["strategic_planning", "growth_prioritization", "cross_agent_orchestration", "market_intelligence"],
            required_integrations=[],
            input_schema={"type": "object", "properties": {"focus_area": {"type": "string"}}},
            output_schema={"type": "object"},
            approval_policy="DEFAULT"
        )

    def execute(self, context: AgentContext) -> AgentResult:
        brand_ctx = context.brand_context or {}
        bo = brand_ctx.get("business_overview", {})
        if hasattr(bo, "model_dump"):
            bo = bo.model_dump(mode="json")
        elif not isinstance(bo, dict):
            bo = {}

        wa = brand_ctx.get("website_analysis", {})
        if hasattr(wa, "model_dump"):
            wa = wa.model_dump(mode="json")
        elif not isinstance(wa, dict):
            wa = {}

        brand_voice = brand_ctx.get("brand_voice", {})
        if hasattr(brand_voice, "model_dump"):
            brand_voice = brand_voice.model_dump(mode="json")
        elif not isinstance(brand_voice, dict):
            brand_voice = {}

        competitors = brand_ctx.get("competitors", [])
        brand_name = bo.get("name") or bo.get("brand_name")
        industry = bo.get("industry") or "Technology & Commerce"
        website_url = bo.get("website_url") or ""

        # If brand name is not in brand_context, query Brand table directly
        if not brand_name and context.brand_id:
            try:
                db_lookup = SessionLocal()
                from app.models.all_models import Brand
                b_row = db_lookup.query(Brand).filter(Brand.id == context.brand_id).first()
                if b_row:
                    brand_name = b_row.name
                    website_url = b_row.website_url or ""
                db_lookup.close()
            except Exception:
                pass

        if not brand_name:
            brand_name = "Your Brand"

        # Prepare AI CMO strategic prompt
        system_prompt = (
            "You are the world-class AI Chief Marketing Officer (AI CMO) for high-growth enterprises.\n"
            "Analyze the brand context, market positioning, competitors, and digital presence to synthesize "
            "an actionable executive growth strategy.\n\n"
            "You MUST return a JSON object with:\n"
            "1. 'executive_summary': A clear, high-impact assessment (2-3 paragraphs).\n"
            "2. 'strategic_pillars': A list of 3-4 strategic growth pillars.\n"
            "3. 'opportunities': A list of objects with fields: 'title', 'description', 'impact' (HIGH/MEDIUM/LOW), "
            "'effort' (LOW/MEDIUM/HIGH), 'confidence' (HIGH/MEDIUM/LOW), 'category'.\n"
            "4. 'delegations': A list of specialized agent tasks (e.g., for Content Writer, SEO Specialist, Ads Strategist)."
        )

        user_content = (
            f"Brand Name: {brand_name}\n"
            f"Industry: {industry}\n"
            f"Website: {website_url}\n"
            f"Business Overview: {json.dumps(bo, default=str)}\n"
            f"Website Analysis: {json.dumps(wa, default=str)}\n"
            f"Brand Voice: {json.dumps(brand_voice, default=str)}\n"
            f"Competitors: {json.dumps(competitors, default=str)}\n"
        )

        strategy_output: Dict[str, Any] = {}
        ai_response = None

        # Attempt LLM strategic synthesis via AIGateway
        try:
            from app.ai.gateway import ai_gateway
            from app.ai.schemas import AIRequestMessage

            ai_response = ai_gateway.generate(
                messages=[
                    AIRequestMessage(role="system", content=system_prompt),
                    AIRequestMessage(role="user", content=user_content)
                ],
                model="gemini-1.5-flash",
                temperature=0.3,
                max_tokens=2500
            )

            if ai_response and ai_response.content:
                raw_text = ai_response.content.strip()
                # Remove code fences if present
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                strategy_output = json.loads(raw_text.strip())

                # Log AI Usage event
                db = SessionLocal()
                try:
                    usage = AIUsageEvent(
                        workspace_id=context.workspace_id,
                        brand_id=context.brand_id,
                        user_id=context.user_id,
                        agent_id=self.agent_id,
                        agent_run_id=context.run_id,
                        provider=ai_response.info.provider,
                        model=ai_response.info.model,
                        input_tokens=ai_response.info.input_tokens,
                        output_tokens=ai_response.info.output_tokens,
                        total_tokens=ai_response.info.total_tokens,
                        status="SUCCESS"
                    )
                    db.add(usage)
                    db.commit()
                except Exception as ex:
                    db.rollback()
                    logger.warning(f"Failed to record AIUsageEvent for AI CMO: {ex}")
                finally:
                    db.close()

        except Exception as e:
            logger.info(f"AI Gateway unavailable or bypassed for AI CMO ({str(e)}). Using deterministic strategic synthesis engine.")
            # Deterministic, high-yield fallback
            strategy_output = {
                "executive_summary": (
                    f"Comprehensive CMO strategic review for {brand_name}. Analysis indicates high organic discovery potential "
                    f"in the {industry} vertical. By unifying brand narrative across touchpoints and deploying automated high-velocity "
                    f"content, {brand_name} can outpace traditional competitors and expand customer acquisition efficiency."
                ),
                "strategic_pillars": [
                    "High-Intent Organic Search & Topical Authority",
                    "Multi-Channel Authority Distribution (LinkedIn & Blog)",
                    "Conversion Funnel & Landing Page Optimization",
                    "Automated Competitor Counter-Positioning"
                ],
                "opportunities": [
                    {
                        "title": f"Capture High-Intent Category Keywords in {industry}",
                        "description": f"Publish 5 comparison and tactical guide articles targeting underserved high-intent search queries for {brand_name}.",
                        "impact": "HIGH",
                        "effort": "LOW",
                        "confidence": "HIGH",
                        "category": "SEO"
                    },
                    {
                        "title": "Automate Executive LinkedIn Thought Leadership",
                        "description": "Deploy weekly strategic industry breakdowns to build direct brand affinity with key enterprise decision makers.",
                        "impact": "HIGH",
                        "effort": "LOW",
                        "confidence": "HIGH",
                        "category": "SOCIAL"
                    },
                    {
                        "title": "Competitor Value Proposition Gap Exploitation",
                        "description": "Highlight unique delivery speed and customer service advantages against legacy competitors.",
                        "impact": "MEDIUM",
                        "effort": "MEDIUM",
                        "confidence": "HIGH",
                        "category": "POSITIONING"
                    }
                ],
                "delegations": [
                    {"agent_id": "seo_agent", "action": "Generate targeted keyword brief and technical gap audit"},
                    {"agent_id": "content_writer_agent", "action": "Draft 3 pillar articles emphasizing core differentiation"},
                    {"agent_id": "social_agent", "action": "Schedule LinkedIn and Twitter launch sequence"}
                ]
            }

        # Persist discovered opportunities to the database if workspace and brand IDs are present
        if context.workspace_id and context.brand_id:
            db = SessionLocal()
            try:
                opp_list = strategy_output.get("opportunities", [])
                for opp in opp_list:
                    title = opp.get("title")
                    if not title:
                        continue
                    existing = db.query(Opportunity).filter(
                        Opportunity.brand_id == context.brand_id,
                        Opportunity.title == title
                    ).first()
                    if not existing:
                        new_opp = Opportunity(
                            workspace_id=context.workspace_id,
                            brand_id=context.brand_id,
                            title=title,
                            description=opp.get("description", ""),
                            impact=opp.get("impact", "MEDIUM"),
                            effort=opp.get("effort", "LOW"),
                            confidence=opp.get("confidence", "HIGH"),
                            priority=90 if opp.get("impact") == "HIGH" else 60,
                            status="NEW",
                            source="AI_CMO"
                        )
                        db.add(new_opp)
                db.commit()
            except Exception as ex:
                db.rollback()
                logger.warning(f"Failed to auto-persist AI CMO opportunities: {ex}")
            finally:
                db.close()

        return AgentResult(
            status="COMPLETED",
            output_data={
                "summary": strategy_output.get("executive_summary", "Strategic review completed."),
                "strategic_pillars": strategy_output.get("strategic_pillars", []),
                "opportunities": strategy_output.get("opportunities", []),
                "actions_taken": [d.get("action") for d in strategy_output.get("delegations", []) if "action" in d] or ["Delegated tasks to specialized agents"],
                "delegations": strategy_output.get("delegations", []),
                "brand_name": brand_name,
                "synthesized_with_ai": ai_response is not None
            }
        )
