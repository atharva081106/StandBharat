"use client"
import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { AuthProvider as IAuthProvider, AgentProvider, DashboardProvider, OpportunityProvider, AiCmoProvider, BrandBrainProvider, NotificationProvider } from './types/interfaces';
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
  notifications: NotificationProvider;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

import { ApiClient } from '../api/client';

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>('loading');
  const [user, setUser] = useState<any | null>(null);
  const [activeWorkspace, setActiveWorkspace] = useState<any | null>(null);
  const [activeBrand, setActiveBrand] = useState<any | null>(null);
  
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);

  const fetchNotifications = async () => {
    if (DATA_MODE === 'api' && ApiClient.defaultHeaders['X-Brand-ID']) {
      try {
        const notifs = await ApiClient.get<any[]>('/api/notifications');
        const unread = await ApiClient.get<any>('/api/notifications/unread-count');
        setNotifications(notifs);
        setUnreadCount(unread.unread_count);
      } catch (e) {}
    }
  };

  const markAsRead = async (id: string) => {
    if (DATA_MODE === 'api') {
      try {
        await ApiClient.patch('/api/notifications/' + id + '/read', {});
        await fetchNotifications();
      } catch (e) {}
    }
  };

  const markAllAsRead = async () => {
    if (DATA_MODE === 'api') {
      try {
        await ApiClient.post('/api/notifications/read-all', {});
        await fetchNotifications();
      } catch (e) {}
    }
  };

  
  const fetchWorkspaceContext = async () => {
    try {
      const workspaces = await ApiClient.get<any[]>('/api/workspaces/');
      if (workspaces.length > 0) {
        const ws = workspaces[0];
        setActiveWorkspace(ws);
        ApiClient.defaultHeaders['X-Workspace-ID'] = ws.id;

        const brands = await ApiClient.get<any[]>('/api/brands/');
        if (brands.length > 0) {
          const br = brands[0];
          setActiveBrand(br);
          ApiClient.defaultHeaders['X-Brand-ID'] = br.id;
        }
      }
      await fetchNotifications();
    } catch (e) {
      console.error("Failed to load workspace context", e);
    }
  };

  const checkAuth = async () => {
    if (DATA_MODE === 'api') {
      try {
        const u = await ApiClient.get<any>('/api/auth/me');
        setUser(u);
        await fetchWorkspaceContext();
        setAuthState('loggedIn');
      } catch (e) {
        setUser(null);
        setAuthState('loggedOut');
      }
    } else {
      if (authState === 'loading') {
        setActiveWorkspace(mockWorkspaces[0]);
        setActiveBrand(mockBrands[0]);
        setAuthState('loggedOut'); // Wait, the original set 'loggedOut' if loading. Let's keep that but set mock contexts.
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
      setActiveWorkspace(mockWorkspaces[0]);
      setActiveBrand(mockBrands[0]);
      setAuthState('loggedIn');
    }
  };

  const signup = async (email: string, password: string, name: string) => {
    if (DATA_MODE === 'api') {
      await ApiClient.post('/api/auth/signup', { email, password, name });
      await login(email, password);
    } else {
      setUser(mockUser);
      setActiveWorkspace(mockWorkspaces[0]);
      setActiveBrand(mockBrands[0]);
      setAuthState('loggedIn');
    }
  };

  const logout = async () => {
    if (DATA_MODE === 'api') {
      try { await ApiClient.post('/api/auth/logout', {}); } catch(e){}
    }
    setUser(null);
    setActiveWorkspace(null);
    setActiveBrand(null);
    ApiClient.defaultHeaders = {};
    setAuthState('loggedOut');
  };
  const [authModalOpen, setAuthModalOpen] = useState<boolean>(false);

  const authImplementation: IAuthProvider = {
    authState,
    setAuthState,
    user,
    activeWorkspace,
    activeBrand,
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
      orchestrator: isApi ? ApiOrchestratorProvider : MockOrchestratorProvider,
      notifications: { notifications, unreadCount, fetchNotifications, markAsRead, markAllAsRead }
    };
  }, [authState, user, activeWorkspace, activeBrand, authModalOpen, notifications, unreadCount]);

  return <AppContext.Provider value={providers}>{children}</AppContext.Provider>;
}

export const useAppProvider = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useAppProvider must be used within AppProvider');
  return context;
}
