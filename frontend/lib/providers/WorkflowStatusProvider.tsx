"use client"
import React, { createContext, useContext, useEffect, useState, ReactNode, useRef } from 'react';
import { useAuth } from './MockProvider';
import { ApiClient } from '../api/client';
import { useBrandBrain } from './MockProvider';
import { useWebsiteAnalysis } from './WebsiteAnalysisProvider';

export interface WorkflowStatus {
  website_analysis: string;
  brand_strategy: string;
  documents_generated: number;
  overall_status: string;
}

interface WorkflowStatusContextType {
  status: WorkflowStatus | null;
  loading: boolean;
  refresh: () => void;
}

const WorkflowStatusContext = createContext<WorkflowStatusContextType | undefined>(undefined);

export const WorkflowStatusProvider = ({ children }: { children: ReactNode }) => {
  const { authState, activeBrand } = useAuth();
  const { refresh: refreshBrandBrain } = useBrandBrain();
  const { refreshAnalysis } = useWebsiteAnalysis();
  
  const refreshBrandBrainRef = useRef(refreshBrandBrain);
  const refreshAnalysisRef = useRef(refreshAnalysis);

  useEffect(() => {
    refreshBrandBrainRef.current = refreshBrandBrain;
    refreshAnalysisRef.current = refreshAnalysis;
  }, [refreshBrandBrain, refreshAnalysis]);

  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [loading, setLoading] = useState(false);

  // We need to keep a stable reference for the manual refresh, but avoid stale closures for the effect
  const fetchStatus = async (brandId: string) => {
    if (process.env.NEXT_PUBLIC_DATA_MODE !== 'api') return null;
    try {
      const data = await ApiClient.get<WorkflowStatus>(`/api/brands/${brandId}/workflow-status`);
      return data;
    } catch (err) {
      console.error("Failed to fetch workflow status", err);
      return null;
    }
  };

  useEffect(() => {
    let timeoutId: NodeJS.Timeout | null = null;
    let isMounted = true;

    const poll = async () => {
      if (authState !== 'loggedIn' || !activeBrand?.id) return;

      const data = await fetchStatus(activeBrand.id);
      if (!isMounted || !data) return;

      setStatus(prev => {
        // If we transition to COMPLETED or FAILED, refresh other contexts
        if (prev?.overall_status === 'PROCESSING' && (data.overall_status === 'COMPLETED' || data.overall_status === 'FAILED')) {
           refreshBrandBrainRef.current();
           refreshAnalysisRef.current();
        }
        return data;
      });

      if (data.overall_status === 'PROCESSING') {
        timeoutId = setTimeout(poll, 3000);
      }
    };

    poll();

    return () => {
      isMounted = false;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [authState, activeBrand?.id]);

  const manualRefresh = () => {
    if (authState === 'loggedIn' && activeBrand?.id) {
       fetchStatus(activeBrand.id).then(data => {
         if (data) setStatus(data);
       });
    }
  };

  return (
    <WorkflowStatusContext.Provider value={{ status, loading, refresh: manualRefresh }}>
      {children}
    </WorkflowStatusContext.Provider>
  );
};

export const useWorkflowStatus = () => {
  const ctx = useContext(WorkflowStatusContext);
  if (!ctx) throw new Error('useWorkflowStatus must be used within WorkflowStatusProvider');
  return ctx;
};
