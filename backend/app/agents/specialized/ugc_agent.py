from app.agents.base import BaseAgent
from app.agents.definition import AgentDefinition
from app.agents.context import AgentContext
from app.agents.result import AgentResult

class UGCAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="ugc_agent",
            name="UGC Agent",
            description="Generates User Generated Content briefs and scripts.",
            capabilities=["brief", "script", "creative_concept"]
        )
        self.definition = AgentDefinition(
            id="ugc_agent",
            name="UGC Agent",
            description="Generates User Generated Content briefs and scripts.",
            category="FUTURE",
            capabilities=["brief", "script", "creative_concept"],
            required_integrations=[],
            input_schema={},
            output_schema={},
            approval_policy="DEFAULT"
        )

    def execute(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            status="NOT_CONFIGURED",
            error="Video generation provider is unavailable."
        )
