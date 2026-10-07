"use client"
import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { AuthProvider as IAuthProvider, AgentProvider, DashboardProvider, OpportunityProvider, AiCmoProvider, BrandBrainProvider } from './types/interfaces';
import { MockAgentProvider } from './mock/MockAgentProvider';
import { MockDashboardProvider } from './mock/MockDashboardProvider';
import { ApiAgentProvider } from './api/ApiAgentProvider';
import { mockUser, mockWorkspaces, mockBrands } from '../mock/data';
import { AuthState } from '../types/auth';
import { MockOpportunityProvider } from './mock/MockOpportunityProvider';
import { ApiDashboardProvider } from './api/ApiDashboardProvider';
import { ApiOpportunityProvider } from './api/ApiOpportunityProvider';
import { MockAiCmoProvider } from './mock/MockAiCmoProvider';
import { ApiAiCmoProvider } from './api/ApiAiCmoProvider';
import { MockBrandBrainProvider } from './mock/MockBrandBrainProvider';
import { ApiBrandBrainProvider } from './api/ApiBrandBrainProvider';
import { OrchestratorProvider } from './types/interfaces';
import { ApiOrchestratorProvider } from './api/ApiOrchestratorProvider';
import { MockOrchestratorProvider } from './mock/MockOrchestratorProvider';

const DATA_MODE = process.env.NEXT_PUBLIC_DATA_MODE || 'mock';

interface AppContextType {
  auth: IAuthProvider;
  agents: AgentProvider;
  dashboard: DashboardProvider;
  opportunity: OpportunityProvider;
  aiCmo: AiCmoProvider;
  brandBrain: BrandBrainProvider;
  orchestrator: OrchestratorProvider;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

import { ApiClient } from '../api/client';

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>('loading');
  const [user, setUser] = useState<any | null>(null);
  
  const checkAuth = async () => {
    if (DATA_MODE === 'api') {
      try {
        const u = await ApiClient.get<any>('/api/auth/me');
        setUser(u);
        setAuthState('loggedIn');
      } catch (e) {
        setUser(null);
        setAuthState('loggedOut');
      }
    } else {
      if (authState === 'loading') {
        setAuthState('loggedOut');
      }
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    if (DATA_MODE === 'api') {
      await ApiClient.post('/api/auth/login', { email, password });
      await checkAuth();
    } else {
      setUser(mockUser);
      setAuthState('loggedIn');
    }
  };

  const signup = async (email: string, password: string, name: string) => {
    if (DATA_MODE === 'api') {
      await ApiClient.post('/api/auth/signup', { email, password, name });
      await login(email, password);
    } else {
      setUser(mockUser);
      setAuthState('loggedIn');
    }
  };

  const logout = async () => {
    if (DATA_MODE === 'api') {
      await ApiClient.post('/api/auth/logout', {});
    }
    setUser(null);
    setAuthState('loggedOut');
  };
  const [authModalOpen, setAuthModalOpen] = useState<boolean>(false);

  const authImplementation: IAuthProvider = {
    authState,
    setAuthState,
    user,
    activeWorkspace: mockWorkspaces[0],
    activeBrand: mockBrands[0],
    login,
    signup,
    logout,
    checkAuth,
    authModalOpen,
    setAuthModalOpen
  };

  const providers = useMemo(() => {
    const isApi = DATA_MODE === 'api';
    return {
      auth: authImplementation,
      agents: isApi ? new ApiAgentProvider() : new MockAgentProvider(),
      dashboard: isApi ? new ApiDashboardProvider() : new MockDashboardProvider(),
      opportunity: isApi ? new ApiOpportunityProvider() : new MockOpportunityProvider(),
      aiCmo: isApi ? new ApiAiCmoProvider() : new MockAiCmoProvider(),
      brandBrain: isApi ? new ApiBrandBrainProvider() : new MockBrandBrainProvider(),
      orchestrator: isApi ? ApiOrchestratorProvider : MockOrchestratorProvider
    };
  }, [authState, user, authModalOpen]);

  return <AppContext.Provider value={providers}>{children}</AppContext.Provider>;
}

export const useAppProvider = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useAppProvider must be used within AppProvider');
  return context;
}
