"use client"
import React from 'react';
import { useAppProvider } from './index';

// Re-export AuthProvider so layout.tsx doesn't break
export { AppProvider as AuthProvider } from './index';

export const useAuth = () => {
  const { auth } = useAppProvider();
  return auth;
}

export const useDashboard = () => {
  const { dashboard } = useAppProvider();
  return dashboard;
}

export const useOpportunity = () => {
  const { opportunity } = useAppProvider();
  return opportunity;
}

export const useOrchestrator = () => {
  const { orchestrator } = useAppProvider();
  return orchestrator;
}
