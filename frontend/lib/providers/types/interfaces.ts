import { AuthState, User } from '../../types/auth'
import { Agent } from '../../types/agent'

export interface AuthProvider {
  authState: AuthState;
  setAuthState: (state: AuthState) => void;
  user: User | null;
  activeWorkspace: any | null;
  activeBrand: any | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  authModalOpen: boolean;
  setAuthModalOpen: (val: boolean) => void;
}

export interface AgentProvider {
  getAgents: () => Promise<Agent[]>;
  getAgent: (id: string) => Promise<Agent>;
  runAgent: (id: string, payload: any) => Promise<any>;
  getAgentRun: (runId: string) => Promise<any>;
  getAgentRuns: (agentId: string) => Promise<any[]>;
}

export interface Opportunity {
  id: string;
  title: string;
  description?: string;
  impact: string;
  confidence: string;
  effort: string;
  priority: number;
  status: string;
  source?: string;
}

export interface KPI {
  label: string;
  value: string;
  change: string;
  trend: string;
}

export interface DashboardProvider {
  getDashboard: () => Promise<{
    kpis: KPI[];
    opportunities: Opportunity[];
    recent_activity: any[];
    system_status: string;
  }>;
}

export interface OpportunityProvider {
  executeOpportunity: (id: string) => Promise<void>;
  dismissOpportunity: (id: string) => Promise<void>;
}

export interface AiCmoProvider {
  chat: (message: string) => Promise<{status: string, response: string}>;
}

export interface BrandBrainProvider {
  getContext: () => Promise<any>;
  updateVoice: (data: any) => Promise<any>;
  addAudience: (data: any) => Promise<any>;
  updateAudience: (id: string, data: any) => Promise<any>;
  deleteAudience: (id: string) => Promise<any>;
  addProduct: (data: any) => Promise<any>;
  updateProduct: (id: string, data: any) => Promise<any>;
  deleteProduct: (id: string) => Promise<any>;
  updatePositioning: (data: any) => Promise<any>;
  addGoal: (data: any) => Promise<any>;
  updateGoal: (id: string, data: any) => Promise<any>;
  deleteGoal: (id: string) => Promise<any>;
  addCompetitor: (data: any) => Promise<any>;
  updateCompetitor: (id: string, data: any) => Promise<any>;
  deleteCompetitor: (id: string) => Promise<any>;
  updateStrategy: (data: any) => Promise<any>;
}

export interface OrchestratorProvider {
  getStatus: () => Promise<any>;
  updateStatus: (mode: string) => Promise<any>;
  getRuns: () => Promise<any[]>;
}
