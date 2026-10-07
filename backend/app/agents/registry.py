from typing import Dict, List
from .base import BaseAgent
from .exceptions import AgentNotFoundException

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        self._agents[agent.agent_id] = agent

    def get_agent(self, agent_id: str) -> BaseAgent:
        if agent_id not in self._agents:
            raise AgentNotFoundException(f"Agent {agent_id} not found")
        return self._agents[agent_id]

    def list_agents(self) -> List[BaseAgent]:
        return list(self._agents.values())

agent_registry = AgentRegistry()

from .test_agent import TestAgent
from .specialized.analytics_agent import AnalyticsAgent
from .specialized.competitor_agent import CompetitorAgent
from .specialized.growth_agent import GrowthAgent
from .specialized.content_strategy_agent import ContentStrategyAgent
from .specialized.content_writer_agent import ContentWriterAgent
from .specialized.performance_agent import PerformanceAgent

agent_registry.register(TestAgent())
agent_registry.register(AnalyticsAgent())
agent_registry.register(CompetitorAgent())
agent_registry.register(GrowthAgent())
agent_registry.register(ContentStrategyAgent())
agent_registry.register(ContentWriterAgent())
agent_registry.register(PerformanceAgent())
