import { AgentProvider } from '../types/interfaces'
import { mockAgents } from '../../mock/data'
import { Agent } from '../../types/agent'

export class MockAgentProvider implements AgentProvider {
  async getAgents(): Promise<Agent[]> {
    return mockAgents as Agent[];
  }
  async getAgent(id: string): Promise<Agent> {
    const agent = mockAgents.find(a => a.id === id);
    if (!agent) throw new Error("Not found");
    return agent as Agent;
  }
  async runAgent(id: string, payload: any): Promise<any> {
    return { id: "mock-run-123", status: "COMPLETED", result_data: { summary: "Mock success" } };
  }
  async getAgentRun(runId: string): Promise<any> {
    return { id: runId, status: "COMPLETED", result_data: { summary: "Mock result" } };
  }
  async getAgentRuns(agentId: string): Promise<any[]> {
    return [
      { id: "mock-run-123", agent_id: agentId, status: "SUCCESS", created_at: new Date(Date.now() - 3600000).toISOString(), result_data: { summary: "Analysis complete. Detected 3 new opportunities." } },
      { id: "mock-run-456", agent_id: agentId, status: "SUCCESS", created_at: new Date(Date.now() - 86400000).toISOString(), result_data: { summary: "Generated content brief for Enterprise AI Marketing." } }
    ];
  }
}
