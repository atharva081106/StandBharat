from app.agents.base import BaseAgent
from app.agents.definition import AgentDefinition
from app.agents.context import AgentContext
from app.agents.result import AgentResult

class RedditAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="reddit_agent",
            name="Reddit Agent",
            description="Manages Reddit engagement.",
            capabilities=["discover", "draft", "publish"]
        )
        self.definition = AgentDefinition(
            id="reddit_agent",
            name="Reddit Agent",
            description="Manages Reddit engagement.",
            category="CHANNEL",
            capabilities=["discover", "draft", "publish"],
            required_integrations=["Reddit"],
            input_schema={},
            output_schema={},
            approval_policy="ALWAYS_REQUIRE"
        )

    def execute(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            status="NOT_CONFIGURED",
            error="Reddit integration is not configured."
        )
