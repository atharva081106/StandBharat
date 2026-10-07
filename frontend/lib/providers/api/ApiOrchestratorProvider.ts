import { OrchestratorProvider } from '../types/interfaces'
import { getOrchestratorStatus, updateOrchestratorStatus, getOrchestratorRuns } from '../../api/orchestrator'

export const ApiOrchestratorProvider: OrchestratorProvider = {
  getStatus: async () => await getOrchestratorStatus(),
  updateStatus: async (mode: string) => await updateOrchestratorStatus(mode),
  getRuns: async () => await getOrchestratorRuns()
}
