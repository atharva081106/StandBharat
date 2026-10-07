import { OrchestratorProvider } from '../types/interfaces'

let mockStatus = { mode: "AUTONOMOUS", last_run_at: new Date(Date.now() - 3600000).toISOString(), next_run_at: new Date(Date.now() + 3600000).toISOString() }
let mockRuns: any[] = [
  { id: "run_1", agent_id: "Analytics Agent", decision: "RUN", reason: "Scheduled weekly data ingestion and metrics tracking.", started_at: new Date(Date.now() - 7200000).toISOString(), status: "SUCCESS" },
  { id: "run_2", agent_id: "Growth Agent", decision: "RUN", reason: "Significant metrics change detected. Generating new hypotheses.", started_at: new Date(Date.now() - 3600000).toISOString(), status: "SUCCESS" },
  { id: "run_3", agent_id: "Content Strategy Agent", decision: "WAIT", reason: "Awaiting human approval on previous briefs before generating more.", started_at: new Date(Date.now() - 1800000).toISOString(), status: "COMPLETED" }
]

export const MockOrchestratorProvider: OrchestratorProvider = {
  getStatus: async () => {
    return Promise.resolve(mockStatus)
  },
  updateStatus: async (mode: string) => {
    mockStatus.mode = mode
    return Promise.resolve(mockStatus)
  },
  getRuns: async () => {
    return Promise.resolve(mockRuns)
  }
}
