import os
from pathlib import Path

BASE_DIR = Path("frontend")

def write_file(path, content):
    full_path = BASE_DIR / path
    os.makedirs(full_path.parent, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. Types
types_common = """
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
}
export interface ApiError {
  message: string;
  code: string;
  status: number;
}
"""
write_file("lib/types/common.ts", types_common)

types_auth = """
export type AuthState = 'loggedOut' | 'loggedIn' | 'onboarding' | 'onboardingComplete';
export interface User {
  id: string;
  name: string;
  email: string;
}
"""
write_file("lib/types/auth.ts", types_auth)

types_agent = """
export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'ACTIVE' | 'WAITING' | 'PAUSED';
}
"""
write_file("lib/types/agent.ts", types_agent)

# 2. API Client Base
api_client = """
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class ApiClient {
  static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${BASE_URL}${endpoint}`
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include' // required for HTTP-only cookies
    })
    
    if (!response.ok) {
      let message = 'API Error'
      try {
        const errData = await response.json()
        message = errData.message || message
      } catch (e) {}
      throw new Error(message)
    }
    return response.json()
  }

  static get<T>(endpoint: string) { return this.request<T>(endpoint, { method: 'GET' }) }
  static post<T>(endpoint: string, body: any) { return this.request<T>(endpoint, { method: 'POST', body: JSON.stringify(body) }) }
  static put<T>(endpoint: string, body: any) { return this.request<T>(endpoint, { method: 'PUT', body: JSON.stringify(body) }) }
  static patch<T>(endpoint: string, body: any) { return this.request<T>(endpoint, { method: 'PATCH', body: JSON.stringify(body) }) }
  static delete<T>(endpoint: string) { return this.request<T>(endpoint, { method: 'DELETE' }) }
}
"""
write_file("lib/api/client.ts", api_client)

api_agents = """
import { ApiClient } from './client'
import { Agent } from '../types/agent'

export const agentsApi = {
  getAgents: () => ApiClient.get<Agent[]>('/api/agents'),
  getAgent: (id: string) => ApiClient.get<Agent>(`/api/agents/${id}`)
}
"""
write_file("lib/api/agents.ts", api_agents)

# 3. Provider Interfaces
provider_interfaces = """
import { AuthState, User } from '../../types/auth'
import { Agent } from '../../types/agent'

export interface AuthProvider {
  authState: AuthState;
  setAuthState: (state: AuthState) => void;
  user: User | null;
  activeWorkspace: any | null;
  activeBrand: any | null;
}

export interface AgentProvider {
  getAgents: () => Promise<Agent[]>;
  getAgent: (id: string) => Promise<Agent>;
}

// Add more domain interfaces as needed
"""
write_file("lib/providers/types/interfaces.ts", provider_interfaces)

# 4. Mock Providers
mock_agent_provider = """
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
}
"""
write_file("lib/providers/mock/MockAgentProvider.ts", mock_agent_provider)

# 5. API Providers
api_agent_provider = """
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
}
"""
write_file("lib/providers/api/ApiAgentProvider.ts", api_agent_provider)

# 6. Provider Factory & Context
providers_index = """
"use client"
import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { AuthProvider as IAuthProvider, AgentProvider } from './types/interfaces';
import { MockAgentProvider } from './mock/MockAgentProvider';
import { ApiAgentProvider } from './api/ApiAgentProvider';
import { mockUser, mockWorkspaces, mockBrands } from '../mock/data';
import { AuthState } from '../types/auth';

const DATA_MODE = process.env.NEXT_PUBLIC_DATA_MODE || 'mock';

interface AppContextType {
  auth: IAuthProvider;
  agents: AgentProvider;
  // Others
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  // Mock Auth State implementation mapped here for backward compatibility
  const [authState, setAuthState] = useState<AuthState>('loggedOut');
  const [user, setUser] = useState<any | null>(null);
  
  useEffect(() => {
    if (authState === 'loggedIn' || authState === 'onboardingComplete') {
      setUser(mockUser);
    } else {
      setUser(null);
    }
  }, [authState]);

  const authImplementation: IAuthProvider = {
    authState,
    setAuthState,
    user,
    activeWorkspace: mockWorkspaces[0],
    activeBrand: mockBrands[0]
  };

  const providers = useMemo(() => {
    const isApi = DATA_MODE === 'api';
    return {
      auth: authImplementation,
      agents: isApi ? new ApiAgentProvider() : new MockAgentProvider()
    };
  }, [authState, user]);

  return <AppContext.Provider value={providers}>{children}</AppContext.Provider>;
}

export const useAppProvider = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useAppProvider must be used within AppProvider');
  return context;
}
"""
write_file("lib/providers/index.tsx", providers_index)

# 7. Bridge existing MockProvider to AppProvider to preserve frontend behavior
mock_provider_bridge = """
"use client"
import React from 'react';
import { useAppProvider } from './index';

// Re-export AuthProvider so layout.tsx doesn't break
export { AppProvider as AuthProvider } from './index';

// Bridge useAuth to use the new context
export const useAuth = () => {
  const { auth } = useAppProvider();
  return auth;
}
"""
write_file("lib/providers/MockProvider.tsx", mock_provider_bridge)

print("Provider architecture created successfully.")
