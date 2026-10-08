from app.agents.base import BaseAgent
from app.agents.definition import AgentDefinition
from app.agents.context import AgentContext
from app.agents.result import AgentResult

class CodingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="coding_agent",
            name="Coding Agent",
            description="Engineering and repository modification.",
            capabilities=["inspect", "patch", "branch", "pull_request"]
        )
        self.definition = AgentDefinition(
            id="coding_agent",
            name="Coding Agent",
            description="Engineering and repository modification.",
            category="EXECUTION",
            capabilities=["inspect", "patch", "branch", "pull_request"],
            required_integrations=["GitHub"],
            input_schema={},
            output_schema={},
            approval_policy="ALWAYS_REQUIRE"
        )

    def execute(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            status="NOT_CONFIGURED",
            error="GitHub integration is not configured."
        )
