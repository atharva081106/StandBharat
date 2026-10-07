import { ApiClient } from './client'

export const getOrchestratorStatus = () => ApiClient.get<any>('/api/orchestrator/status')
export const updateOrchestratorStatus = (mode: string) => ApiClient.patch<any>('/api/orchestrator/status', { mode })
export const getOrchestratorRuns = () => ApiClient.get<any[]>('/api/orchestrator/runs')
