import { ApiClient } from './client'
import { Agent } from '../types/agent'

export const agentsApi = {
  getAgents: () => ApiClient.get<Agent[]>('/api/agents'),
  getAgent: (id: string) => ApiClient.get<Agent>(`/api/agents/${id}`),
  runAgent: (id: string, payload: any) => ApiClient.post<any>(`/api/agents/${id}/run`, payload),
  getAgentRun: (runId: string) => ApiClient.get<any>(`/api/agent-runs/${runId}`),
  getAgentRuns: (agentId: string) => ApiClient.get<any[]>(`/api/agent-runs?agent_id=${agentId}`)
}
