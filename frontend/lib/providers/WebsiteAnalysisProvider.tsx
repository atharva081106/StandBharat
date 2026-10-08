"use client"
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getCookie } from 'cookies-next';
import { useAuth, useDashboard } from './MockProvider';

export type WebsiteAnalysisStatus = 'NOT_ANALYZED' | 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface WebsiteAnalysisData {
  id: string;
  status: WebsiteAnalysisStatus;
  url: string | null;
  result_metadata: {
    final_url?: string;
    http_status?: number;
    https?: boolean;
    title?: string;
    title_length?: number;
    meta_description?: string;
    meta_description_exists?: boolean;
    canonical_exists?: boolean;
    canonical_url?: string;
    h1_count?: number;
    h1_exists?: boolean;
    h1_first?: string;
    h2_count?: number;
    open_graph_exists?: boolean;
    language?: string;
    word_count?: number;
    internal_links?: number;
    external_links?: number;
    image_count?: number;
    images_missing_alt?: number;
    robots_exists?: boolean;
    sitemap_exists?: boolean;
  } | null;
  analysis_results: any;
  errors: any;
}

interface WebsiteAnalysisContextType {
  analysis: WebsiteAnalysisData | null;
  loading: boolean;
  error: string | null;
  triggerAnalysis: () => Promise<void>;
  refreshAnalysis: () => Promise<void>;
}

const WebsiteAnalysisContext = createContext<WebsiteAnalysisContextType | undefined>(undefined);

export function WebsiteAnalysisProvider({ children }: { children: ReactNode }) {
  const { activeWorkspace, activeBrand } = useAuth();
  const [analysis, setAnalysis] = useState<WebsiteAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const mode = process.env.NEXT_PUBLIC_DATA_MODE || 'api';

  const fetchAnalysis = async () => {
    if (!activeWorkspace || !activeBrand) return;

    if (mode === 'mock') {
      // Mock Data Mode
      setAnalysis({
        id: 'mock-123',
        status: 'COMPLETED',
        url: activeBrand.website_url || 'https://example.com',
        result_metadata: {
          title: 'Mock Website',
          meta_description_exists: true,
          h1_exists: true,
          internal_links: 12,
          external_links: 4,
          word_count: 500,
          robots_exists: true,
          sitemap_exists: true,
          https: true
        },
        analysis_results: {},
        errors: null
      });
      setLoading(false);
      return;
    }

    // API Mode
    try {
      const token = getCookie('access_token');
      if (!token) return;

      const res = await fetch(`http://localhost:8000/api/brands/${activeBrand.id}/website-analysis`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Workspace-Id': activeWorkspace.id,
          'X-Brand-Id': activeBrand.id
        }
      });

      if (!res.ok) {
        throw new Error('Failed to fetch website analysis');
      }

      const data = await res.json();
      setAnalysis(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const triggerAnalysis = async () => {
    if (!activeWorkspace || !activeBrand) return;

    if (mode === 'mock') {
      setAnalysis(prev => prev ? { ...prev, status: 'RUNNING' } : null);
      setTimeout(() => {
        setAnalysis(prev => prev ? { ...prev, status: 'COMPLETED' } : null);
      }, 2000);
      return;
    }

    try {
      const token = getCookie('access_token');
      if (!token) return;

      const res = await fetch(`http://localhost:8000/api/brands/${activeBrand.id}/website-analysis`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Workspace-Id': activeWorkspace.id,
          'X-Brand-Id': activeBrand.id
        }
      });

      if (!res.ok) {
        throw new Error('Failed to trigger analysis');
      }

      const data = await res.json();
      setAnalysis(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, [activeWorkspace?.id, activeBrand?.id, mode]);

  // Poll if running
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (analysis?.status === 'RUNNING' || analysis?.status === 'QUEUED') {
      interval = setInterval(() => {
        fetchAnalysis();
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [analysis?.status]);

  return (
    <WebsiteAnalysisContext.Provider value={{ analysis, loading, error, triggerAnalysis, refreshAnalysis: fetchAnalysis }}>
      {children}
    </WebsiteAnalysisContext.Provider>
  );
}

export function useWebsiteAnalysis() {
  const context = useContext(WebsiteAnalysisContext);
  if (context === undefined) {
    throw new Error('useWebsiteAnalysis must be used within a WebsiteAnalysisProvider');
  }
  return context;
}
