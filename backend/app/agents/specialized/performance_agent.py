import json
import traceback
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.agents.context import AgentContext
from app.agents.result import AgentResult
from app.models.all_models import Opportunity, AIUsageEvent
from app.models.performance import PerformanceSnapshot
from app.db.session import SessionLocal
from app.ai.gateway import ai_gateway
from app.ai.schemas import AIRequestMessage
from app.ai.exceptions import AINotConfiguredException

class PerformanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="performance",
            name="Performance Intelligence Agent",
            description="Analyzes publishing performance data to generate structured signals and opportunities.",
            capabilities=["performance_analysis", "opportunity_generation"]
        )
    
    def execute(self, context: AgentContext) -> AgentResult:
        result = AgentResult(
            status="SUCCESS",
            output_data={"findings": {}, "actions_taken": []}
        )
        
        db = SessionLocal()
        try:
            # Get recent performance data
            snapshots = db.query(PerformanceSnapshot).filter(
                PerformanceSnapshot.workspace_id == context.workspace_id,
                PerformanceSnapshot.brand_id == context.brand_id,
                PerformanceSnapshot.source_status == "SUCCESS"
            ).order_by(PerformanceSnapshot.captured_at.desc()).limit(50).all()
            
            if not snapshots:
                result.output_data["findings"]["message"] = "No performance data available for analysis"
                return result
                
            snapshot_data = []
            for s in snapshots:
                snapshot_data.append({
                    "channel": s.channel,
                    "impressions": s.impressions,
                    "engagements": s.engagements,
                    "engagement_rate": s.engagement_rate,
                    "captured_at": str(s.captured_at)
                })
                
            prompt = f"""
            Analyze the following recent performance data for the brand.
            
            Data:
            {json.dumps(snapshot_data, indent=2)}
            
            Generate structured performance signals. 
            A signal should have:
            - type: e.g. HIGH_PERFORMER, LOW_PERFORMER, ENGAGEMENT_TREND
            - confidence: HIGH, MEDIUM, LOW
            - observation: what you observed in the data
            - interpretation: what this means
            - recommendation: what action should be taken
            
            Also, if there are strong recommendations, formulate them as Growth Opportunities.
            An opportunity should have:
            - title: concise title
            - description: detailed description of the opportunity based on the signal
            - impact: HIGH, MEDIUM, LOW
            - confidence: HIGH, MEDIUM, LOW
            - effort: HIGH, MEDIUM, LOW
            
            Return JSON strictly matching this schema:
            {{
                "signals": [
                    {{
                        "type": "string",
                        "confidence": "string",
                        "observation": "string",
                        "interpretation": "string",
                        "recommendation": "string"
                    }}
                ],
                "opportunities": [
                    {{
                        "title": "string",
                        "description": "string",
                        "impact": "string",
                        "confidence": "string",
                        "effort": "string"
                    }}
                ]
            }}
            """
            
            try:
                ai_gateway._get_provider()
            except AINotConfiguredException:
                result.status = "error"
                result.error = "AI not configured"
                return result

            res = ai_gateway.generate(
                messages=[
                    AIRequestMessage(role="system", content="You are a data-driven Performance Intelligence Agent. You only state facts derived from the data provided. Output valid JSON only."),
                    AIRequestMessage(role="user", content=prompt)
                ]
            )
            
            # Log usage
            usage = AIUsageEvent(
                workspace_id=context.workspace_id,
                user_id=context.user_id,
                agent_id=self.agent_id,
                provider=ai_gateway._get_provider().get_name(),
                model=ai_gateway._get_provider().default_model,
                input_tokens=res.usage.prompt_tokens if res.usage else 0,
                output_tokens=res.usage.completion_tokens if res.usage else 0,
                status="SUCCESS"
            )
            db.add(usage)
            db.commit()

            try:
                # Strip backticks if present
                content = res.content
                if content.startswith("```json"):
                    content = content[7:-3]
                parsed = json.loads(content)
            except Exception as e:
                result.status = "error"
                result.error = f"Failed to parse LLM response: {str(e)}"
                return result
                
            result.output_data["findings"]["signals"] = parsed.get("signals", [])
            
            created_opportunities = []
            for opp_data in parsed.get("opportunities", []):
                existing = db.query(Opportunity).filter(
                    Opportunity.workspace_id == context.workspace_id,
                    Opportunity.brand_id == context.brand_id,
                    Opportunity.title == opp_data.get("title")
                ).first()
                
                if not existing:
                    opp = Opportunity(
                        workspace_id=context.workspace_id,
                        brand_id=context.brand_id,
                        title=opp_data.get("title"),
                        description=opp_data.get("description"),
                        impact=opp_data.get("impact"),
                        confidence=opp_data.get("confidence"),
                        effort=opp_data.get("effort"),
                        source="performance_agent"
                    )
                    db.add(opp)
                    created_opportunities.append(opp_data.get("title"))
                    
            db.commit()
            
            result.output_data["findings"]["opportunities_created"] = len(created_opportunities)
            if created_opportunities:
                result.output_data["actions_taken"].append(f"Created {len(created_opportunities)} opportunities")
            
            return result
            
        except Exception as e:
            traceback.print_exc()
            result.status = "error"
            result.error = str(e)
            return result
        finally:
            db.close()
