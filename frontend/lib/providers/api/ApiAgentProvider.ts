import { AgentProvider } from '../types/interfaces'
import { agentsApi } from '../../api/agents'
import { Agent } from '../../types/agent'

export class ApiAgentProvider implements AgentProvider {
  async getAgents(): Promise<Agent[]> {
    return agentsApi.getAgents();
  }
  async getAgent(id: string): Promise<Agent> {
    return agentsApi.getAgent(id);
  }
  async runAgent(id: string, payload: any): Promise<any> {
    return agentsApi.runAgent(id, payload);
  }
  async getAgentRun(runId: string): Promise<any> {
    return agentsApi.getAgentRun(runId);
  }
  async getAgentRuns(agentId?: string): Promise<any[]> {
    return agentsApi.getAgentRuns(agentId);
  }
}
