from app.agents.base import BaseAgent
from app.agents.definition import AgentDefinition
from app.agents.context import AgentContext
from app.agents.result import AgentResult

class LinkedInAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="linkedin_agent",
            name="LinkedIn Agent",
            description="Manages LinkedIn publishing and performance.",
            capabilities=["draft", "publish", "metrics"]
        )
        self.definition = AgentDefinition(
            id="linkedin_agent",
            name="LinkedIn Agent",
            description="Manages LinkedIn publishing and performance.",
            category="CHANNEL",
            capabilities=["draft", "publish", "metrics"],
            required_integrations=["LinkedIn"],
            input_schema={},
            output_schema={},
            approval_policy="ALWAYS_REQUIRE"
        )

    def execute(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            status="NOT_CONFIGURED",
            error="LinkedIn integration is not configured."
        )
