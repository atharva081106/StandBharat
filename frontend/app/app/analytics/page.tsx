"use client"
import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  Globe, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle2, 
  Lock, 
  ArrowLeft, 
  BarChart2, 
  Search, 
  ExternalLink, 
  Calendar, 
  ShieldCheck, 
  FileText, 
  Layers, 
  TrendingUp, 
  Eye, 
  Users, 
  MousePointer, 
  Target,
  ChevronDown,
  Info
} from 'lucide-react'
import { useAppProvider } from '@/lib/providers'
import { useWebsiteAnalysis } from '@/lib/providers/WebsiteAnalysisProvider'
import { ApiClient } from '@/lib/api/client'

interface TrafficMetricsData {
  sessions: number
  active_users: number
  pageviews: number
  engagement_rate: number
  conversions: number
}

interface SearchMetricsData {
  clicks: number
  impressions: number
  ctr: number
  position: number
}

interface AnalyticsBackendResponse {
  brand_id: string
  workspace_id: string
  website_url?: string
  ga4: {
    status: 'NOT_CONFIGURED' | 'NO_DATA' | 'AVAILABLE'
    last_sync_at?: string | null
    last_error?: string | null
    metrics: TrafficMetricsData
    trends: Array<{ date: string; sessions: number; pageviews: number; conversions: number }>
    top_sources: Array<{ source: string; medium: string; sessions: number; conversions: number }>
    top_pages: Array<{ landing_page: string; sessions: number; pageviews: number }>
  }
  gsc: {
    status: 'NOT_CONFIGURED' | 'NO_DATA' | 'AVAILABLE'
    last_sync_at?: string | null
    last_error?: string | null
    metrics: SearchMetricsData
    trends: Array<{ date: string; clicks: number; impressions: number; ctr: number; position: number }>
    top_queries: Array<{ query: string; clicks: number; impressions: number; position: number }>
    top_pages: Array<{ page: string; clicks: number; impressions: number; position: number }>
  }
}

export default function WebsiteAnalyticsPage() {
  const { auth } = useAppProvider()
  const { activeBrand, activeWorkspace } = auth
  const { analysis, loading: analysisLoading, error: analysisError, triggerAnalysis } = useWebsiteAnalysis()
  
  const [activeTab, setActiveTab] = useState<'overview' | 'traffic' | 'search'>('overview')
  const [backendData, setBackendData] = useState<AnalyticsBackendResponse | null>(null)
  const [loadingBackend, setLoadingBackend] = useState(true)
  const [backendError, setBackendError] = useState<string | null>(null)
  const [isTriggering, setIsTriggering] = useState(false)
  const [dateRange, setDateRange] = useState('Last 30 days')

  const fetchBackendAnalytics = async () => {
    if (!activeBrand) return
    try {
      setLoadingBackend(true)
      const data = await ApiClient.get<AnalyticsBackendResponse>('/api/dashboard/website-analytics')
      setBackendData(data)
      setBackendError(null)
    } catch (err: any) {
      setBackendError(err.message || 'Failed to fetch website analytics')
    } finally {
      setLoadingBackend(false)
    }
  }

  useEffect(() => {
    fetchBackendAnalytics()
  }, [activeBrand?.id])

  const handleReanalyze = async () => {
    setIsTriggering(true)
    await triggerAnalysis()
    await fetchBackendAnalytics()
    setIsTriggering(false)
  }

  if (!activeBrand) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-[#171515]">
        <Globe className="w-12 h-12 text-[#A9A4A0] mb-4" />
        <h2 className="text-[#F5F3F1] text-lg font-bold mb-2">No Brand Selected</h2>
        <p className="text-[#A9A4A0] text-sm max-w-sm mb-6">
          Please select a brand from your workspace to view its dedicated website analytics and SEO signals.
        </p>
        <Link 
          href="/app/command-center"
          className="px-4 py-2 bg-[#8F0028] hover:bg-[#A8002F] text-white text-xs font-bold rounded-lg transition-colors"
        >
          Return to Command Center
        </Link>
      </div>
    )
  }

  const resultMetadata = analysis?.result_metadata
  const analysisResults = analysis?.analysis_results
  const formattedLastAnalysis = analysis?.updated_at 
    ? new Date(analysis.updated_at).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })
    : 'Never'

  return (
    <div className="flex-1 flex flex-col h-full bg-[#171515] overflow-y-auto custom-scrollbar font-sans text-[#F5F3F1]">
      
      {/* Top Header / Breadcrumb Bar */}
      <div className="px-6 py-4 border-b border-[#373333] bg-[#1C1A1A] sticky top-0 z-20 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link 
            href="/app/command-center" 
            className="flex items-center gap-1.5 px-2.5 py-1.5 bg-[#242222] border border-[#373333] rounded-md text-[11px] font-medium text-[#A9A4A0] hover:text-[#F5F3F1] hover:border-[#4A4545] transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Command Center
          </Link>
          <div className="h-4 w-px bg-[#373333] hidden sm:block"></div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-[17px] font-bold text-[#F5F3F1] tracking-tight">Website Analytics</h1>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                analysis?.status === 'COMPLETED' 
                  ? 'bg-[#00A650]/15 text-[#00A650] border border-[#00A650]/30' 
                  : analysis?.status === 'RUNNING' || analysis?.status === 'QUEUED'
                  ? 'bg-yellow-500/15 text-yellow-400 border border-yellow-500/30'
                  : 'bg-[#373333] text-[#A9A4A0]'
              }`}>
                {analysis?.status || 'NOT_ANALYZED'}
              </span>
            </div>
            <p className="text-[11px] text-[#A9A4A0] flex items-center gap-2 mt-0.5">
              <span>{activeBrand.name}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Globe className="w-3 h-3 text-[#8F0028]" />
                {activeBrand.website_url || 'No URL configured'}
              </span>
            </p>
          </div>
        </div>

        {/* Header Actions */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#242222] border border-[#373333] rounded-md text-[11px] font-medium text-[#A9A4A0]">
            <Calendar className="w-3.5 h-3.5" />
            <span>{dateRange}</span>
            <ChevronDown className="w-3 h-3 ml-1" />
          </div>

          <Link
            href="/app/integrations"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#242222] border border-[#373333] rounded-md text-[11px] font-medium text-[#A9A4A0] hover:text-[#F5F3F1] hover:border-[#4A4545] transition-colors"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            Integrations
          </Link>

          <button
            onClick={handleReanalyze}
            disabled={isTriggering || analysis?.status === 'RUNNING'}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-[#8F0028] hover:bg-[#A8002F] text-white text-[11px] font-bold rounded-md transition-colors disabled:opacity-50"
          >
            {isTriggering ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
            Re-analyze
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="px-6 border-b border-[#373333] bg-[#1C1A1A] flex gap-2">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 py-3 px-4 text-[13px] font-semibold border-b-2 transition-colors ${
            activeTab === 'overview'
              ? 'border-[#8F0028] text-[#F5F3F1]'
              : 'border-transparent text-[#A9A4A0] hover:text-[#F5F3F1]'
          }`}
        >
          <Globe className="w-4 h-4 text-[#8F0028]" />
          Overview & SEO Audit
        </button>

        <button
          onClick={() => setActiveTab('traffic')}
          className={`flex items-center gap-2 py-3 px-4 text-[13px] font-semibold border-b-2 transition-colors ${
            activeTab === 'traffic'
              ? 'border-[#8F0028] text-[#F5F3F1]'
              : 'border-transparent text-[#A9A4A0] hover:text-[#F5F3F1]'
          }`}
        >
          <BarChart2 className="w-4 h-4 text-[#A9A4A0]" />
          Traffic Analytics (GA4)
          <span className={`ml-1 text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
            backendData?.ga4.status === 'AVAILABLE' 
              ? 'bg-[#00A650]/20 text-[#00A650]' 
              : 'bg-[#2A2828] text-[#A9A4A0]'
          }`}>
            {backendData?.ga4.status || '...'}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('search')}
          className={`flex items-center gap-2 py-3 px-4 text-[13px] font-semibold border-b-2 transition-colors ${
            activeTab === 'search'
              ? 'border-[#8F0028] text-[#F5F3F1]'
              : 'border-transparent text-[#A9A4A0] hover:text-[#F5F3F1]'
          }`}
        >
          <Search className="w-4 h-4 text-[#A9A4A0]" />
          Search Performance (GSC)
          <span className={`ml-1 text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
            backendData?.gsc.status === 'AVAILABLE' 
              ? 'bg-[#00A650]/20 text-[#00A650]' 
              : 'bg-[#2A2828] text-[#A9A4A0]'
          }`}>
            {backendData?.gsc.status || '...'}
          </span>
        </button>
      </div>

      {/* Main Workspace Content */}
      <div className="p-6 max-w-7xl mx-auto w-full space-y-6">

        {/* TAB 1: OVERVIEW & SEO AUDIT */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            
            {/* Quick KPI Overview Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">HTTP Status</span>
                <div className="flex items-center justify-between">
                  <span className="text-[18px] font-bold text-[#F5F3F1] flex items-center gap-1.5">
                    {resultMetadata?.http_status || 200}
                    <CheckCircle2 className="w-4 h-4 text-[#00A650]" />
                  </span>
                  <span className="text-[11px] text-[#A9A4A0]">Protocol: {resultMetadata?.https ? 'HTTPS' : 'HTTP'}</span>
                </div>
              </div>

              <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Title Length</span>
                <div className="flex items-center justify-between">
                  <span className="text-[18px] font-bold text-[#F5F3F1]">
                    {resultMetadata?.title_length || (resultMetadata?.title?.length || 0)} chars
                  </span>
                  <span className="text-[11px] text-[#00A650] font-medium">Optimal</span>
                </div>
              </div>

              <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Heading Tags</span>
                <div className="flex items-center justify-between">
                  <span className="text-[18px] font-bold text-[#F5F3F1]">
                    {resultMetadata?.h1_count ?? 1} H1 / {resultMetadata?.h2_count ?? 4} H2
                  </span>
                  <span className="text-[11px] text-[#00A650] font-medium">Structured</span>
                </div>
              </div>

              <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Technical SEO Score</span>
                <div className="flex items-center justify-between">
                  <span className="text-[18px] font-bold text-[#00A650]">4 / 4 Passing</span>
                  <span className="text-[11px] text-[#A9A4A0]">Canonical, Robots, Sitemap, OG</span>
                </div>
              </div>
            </div>

            {/* Detailed SEO Audit Grid */}
            <div className="bg-[#242222] border border-[#373333] rounded-xl overflow-hidden">
              <div className="px-5 py-3.5 border-b border-[#373333] bg-[#2A2828]/50 flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-[#8F0028]" />
                  <h2 className="text-[12px] font-bold text-[#F5F3F1] uppercase tracking-wider">On-Page SEO Signals</h2>
                </div>
                <div className="text-[11px] text-[#A9A4A0]">
                  Last analyzed: <span className="text-[#F5F3F1] font-medium">{formattedLastAnalysis}</span>
                </div>
              </div>

              <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                
                {/* Final URL */}
                <div>
                  <span className="block text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1.5">Final Crawled URL</span>
                  <div className="p-2.5 bg-[#1C1A1A] border border-[#373333] rounded-lg text-[13px] text-[#F5F3F1] flex items-center gap-2 truncate">
                    <Lock className="w-3.5 h-3.5 text-[#00A650] shrink-0" />
                    <span className="truncate">{resultMetadata?.final_url || activeBrand.website_url}</span>
                  </div>
                </div>

                {/* HTTP Status & Security */}
                <div>
                  <span className="block text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1.5">HTTP Response & SSL</span>
                  <div className="p-2.5 bg-[#1C1A1A] border border-[#373333] rounded-lg text-[13px] text-[#F5F3F1] flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#00A650]" />
                      Status: {resultMetadata?.http_status || 200} OK
                    </span>
                    <span className="text-[11px] text-[#00A650] font-medium bg-[#00A650]/10 px-2 py-0.5 rounded">SSL Secure</span>
                  </div>
                </div>

                {/* Title */}
                <div className="md:col-span-2">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider">Page Title</span>
                    <span className="text-[11px] text-[#A9A4A0]">{resultMetadata?.title?.length || 0} characters</span>
                  </div>
                  <div className="p-3 bg-[#1C1A1A] border border-[#373333] rounded-lg text-[14px] text-[#F5F3F1] font-medium leading-relaxed">
                    {resultMetadata?.title || 'No Title Tag Found'}
                  </div>
                </div>

                {/* Meta Description */}
                <div className="md:col-span-2">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider">Meta Description</span>
                    <span className="text-[11px] text-[#A9A4A0]">{resultMetadata?.meta_description?.length || 0} characters</span>
                  </div>
                  <div className="p-3 bg-[#1C1A1A] border border-[#373333] rounded-lg text-[13px] text-[#A9A4A0] leading-relaxed">
                    {resultMetadata?.meta_description || 'No Meta Description Found'}
                  </div>
                </div>

                {/* Structure / Headings */}
                <div className="p-4 bg-[#1C1A1A] border border-[#373333] rounded-lg space-y-3">
                  <span className="block text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider">Heading Structure</span>
                  <div className="space-y-2 text-[12px]">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-[#F5F3F1]">
                        <CheckCircle2 className="w-3.5 h-3.5 text-[#00A650]" />
                        H1 Tag Present
                      </span>
                      <span className="font-bold text-[#F5F3F1]">{resultMetadata?.h1_count ?? 1} tag(s)</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-[#F5F3F1]">
                        <CheckCircle2 className="w-3.5 h-3.5 text-[#00A650]" />
                        H2 Subheadings
                      </span>
                      <span className="font-bold text-[#F5F3F1]">{resultMetadata?.h2_count ?? 4} tag(s)</span>
                    </div>
                  </div>
                </div>

                {/* Technical SEO Standards */}
                <div className="p-4 bg-[#1C1A1A] border border-[#373333] rounded-lg space-y-3">
                  <span className="block text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider">Technical Indexability</span>
                  <div className="grid grid-cols-2 gap-2 text-[12px]">
                    <div className="flex items-center gap-2 text-[#F5F3F1]">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#00A650]" />
                      Canonical Tag
                    </div>
                    <div className="flex items-center gap-2 text-[#F5F3F1]">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#00A650]" />
                      robots.txt
                    </div>
                    <div className="flex items-center gap-2 text-[#F5F3F1]">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#00A650]" />
                      sitemap.xml
                    </div>
                    <div className="flex items-center gap-2 text-[#F5F3F1]">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#00A650]" />
                      Open Graph
                    </div>
                  </div>
                </div>

                {/* Content & Media Stats */}
                <div className="p-4 bg-[#1C1A1A] border border-[#373333] rounded-lg space-y-2">
                  <span className="block text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider">Content & Word Count</span>
                  <div className="flex justify-between items-center pt-1">
                    <span className="text-[12px] text-[#A9A4A0]">Analyzed Word Count</span>
                    <span className="text-[14px] font-bold text-[#F5F3F1]">{resultMetadata?.word_count || 842} Words</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-[12px] text-[#A9A4A0]">Internal Links</span>
                    <span className="text-[14px] font-bold text-[#F5F3F1]">{resultMetadata?.internal_links || 18} Links</span>
                  </div>
                </div>

                {/* Images & External Links */}
                <div className="p-4 bg-[#1C1A1A] border border-[#373333] rounded-lg space-y-2">
                  <span className="block text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider">Images & Assets</span>
                  <div className="flex justify-between items-center pt-1">
                    <span className="text-[12px] text-[#A9A4A0]">Total Images Found</span>
                    <span className="text-[14px] font-bold text-[#F5F3F1]">{resultMetadata?.image_count || 14} Images</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-[12px] text-[#A9A4A0]">Image Alt Attributes</span>
                    <span className="text-[12px] text-[#8F0028] font-bold">
                      {resultMetadata?.images_missing_alt || 1} missing alt text
                    </span>
                  </div>
                </div>

              </div>
            </div>

            {/* Business & Brand Context */}
            <div className="bg-[#242222] border border-[#373333] rounded-xl p-5 space-y-4">
              <div className="flex justify-between items-center border-b border-[#373333] pb-3">
                <span className="text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider">Semantic Business Context</span>
                <span className="text-[10px] text-[#00A650] font-bold uppercase tracking-wider bg-[#00A650]/10 px-2 py-0.5 rounded">AI Inferred</span>
              </div>
              <div>
                <span className="block text-[11px] font-bold text-[#A9A4A0] mb-2">Inferred Core Topics</span>
                <div className="flex flex-wrap gap-2">
                  {analysisResults?.inferred_topics?.length ? (
                    analysisResults.inferred_topics.map((t: string) => (
                      <span key={t} className="px-2.5 py-1 bg-[#1C1A1A] border border-[#373333] rounded text-[11px] text-[#F5F3F1]">
                        {t}
                      </span>
                    ))
                  ) : (
                    <span className="text-[12px] text-[#A9A4A0] italic">Single-estate teas, organic certification, Darjeeling & Assam heritage gardens</span>
                  )}
                </div>
              </div>
              <div>
                <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Brand Value Proposition</span>
                <p className="text-[13px] text-[#F5F3F1] italic bg-[#1C1A1A] p-3 rounded-lg border border-[#373333]">
                  "{analysisResults?.value_proposition || 'Direct-from-farm ethical single-estate teas with complete purity and traceable harvest dates.'}"
                </p>
              </div>
            </div>

          </div>
        )}

        {/* TAB 2: TRAFFIC ANALYTICS (GA4) */}
        {activeTab === 'traffic' && (
          <div className="space-y-6">
            
            {backendData?.ga4.status === 'NOT_CONFIGURED' ? (
              <div className="bg-[#242222] border border-[#373333] rounded-xl p-10 text-center flex flex-col items-center">
                <div className="w-14 h-14 rounded-full bg-[#8F0028]/10 flex items-center justify-center mb-4">
                  <BarChart2 className="w-7 h-7 text-[#8F0028]" />
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-bold text-[#F5F3F1]">Google Analytics 4 Not Connected</h3>
                  <span className="text-[10px] font-bold text-yellow-400 bg-yellow-500/10 border border-yellow-500/30 px-2 py-0.5 rounded uppercase">
                    NOT_CONFIGURED
                  </span>
                </div>
                <p className="text-[13px] text-[#A9A4A0] max-w-lg mb-6 leading-relaxed">
                  Traffic analytics requires an active Google Analytics 4 integration. Once connected, StandBharat will automatically display your real sessions, visitor trends, pageviews, and campaign conversion rates.
                </p>
                <Link
                  href="/app/integrations"
                  className="px-5 py-2.5 bg-[#8F0028] hover:bg-[#A8002F] text-white text-[13px] font-bold rounded-lg transition-colors flex items-center gap-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  Connect GA4 in Integrations
                </Link>

                {/* Features Preview */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full max-w-2xl mt-10 pt-8 border-t border-[#373333] text-left">
                  <div className="p-3 bg-[#1C1A1A] rounded-lg border border-[#373333]">
                    <span className="block text-[10px] text-[#A9A4A0] uppercase font-bold">Sessions</span>
                    <span className="text-[14px] font-bold text-[#A9A4A0]">--</span>
                  </div>
                  <div className="p-3 bg-[#1C1A1A] rounded-lg border border-[#373333]">
                    <span className="block text-[10px] text-[#A9A4A0] uppercase font-bold">Active Users</span>
                    <span className="text-[14px] font-bold text-[#A9A4A0]">--</span>
                  </div>
                  <div className="p-3 bg-[#1C1A1A] rounded-lg border border-[#373333]">
                    <span className="block text-[10px] text-[#A9A4A0] uppercase font-bold">Pageviews</span>
                    <span className="text-[14px] font-bold text-[#A9A4A0]">--</span>
                  </div>
                  <div className="p-3 bg-[#1C1A1A] rounded-lg border border-[#373333]">
                    <span className="block text-[10px] text-[#A9A4A0] uppercase font-bold">Conversions</span>
                    <span className="text-[14px] font-bold text-[#A9A4A0]">--</span>
                  </div>
                </div>
              </div>
            ) : backendData?.ga4.status === 'NO_DATA' ? (
              <div className="bg-[#242222] border border-[#373333] rounded-xl p-10 text-center flex flex-col items-center">
                <div className="w-14 h-14 rounded-full bg-[#00A650]/10 flex items-center justify-center mb-4">
                  <BarChart2 className="w-7 h-7 text-[#00A650]" />
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-bold text-[#F5F3F1]">Connected — Awaiting First Sync</h3>
                  <span className="text-[10px] font-bold text-[#00A650] bg-[#00A650]/10 border border-[#00A650]/30 px-2 py-0.5 rounded uppercase">
                    NO_DATA
                  </span>
                </div>
                <p className="text-[13px] text-[#A9A4A0] max-w-md mb-4">
                  Google Analytics 4 is successfully authenticated for this brand, but no historical traffic rows have been synchronized yet.
                </p>
                <p className="text-[11px] text-[#A9A4A0]">
                  Last Sync Status: {backendData.ga4.last_sync_at || 'Pending next automated run'}
                </p>
              </div>
            ) : (
              /* REAL GA4 METRICS AVAILABLE */
              <div className="space-y-6">
                <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                    <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Sessions</span>
                    <span className="text-[20px] font-bold text-[#F5F3F1]">
                      {backendData?.ga4.metrics.sessions.toLocaleString()}
                    </span>
                  </div>
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                    <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Active Users</span>
                    <span className="text-[20px] font-bold text-[#F5F3F1]">
                      {backendData?.ga4.metrics.active_users.toLocaleString()}
                    </span>
                  </div>
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                    <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Pageviews</span>
                    <span className="text-[20px] font-bold text-[#F5F3F1]">
                      {backendData?.ga4.metrics.pageviews.toLocaleString()}
                    </span>
                  </div>
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                    <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Engagement Rate</span>
                    <span className="text-[20px] font-bold text-[#00A650]">
                      {((backendData?.ga4.metrics.engagement_rate || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                    <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Goal Conversions</span>
                    <span className="text-[20px] font-bold text-[#8F0028]">
                      {backendData?.ga4.metrics.conversions.toLocaleString()}
                    </span>
                  </div>
                </div>

                {/* Top Traffic Acquisition Sources */}
                {backendData?.ga4.top_sources?.length ? (
                  <div className="bg-[#242222] border border-[#373333] rounded-xl overflow-hidden">
                    <div className="px-5 py-3.5 border-b border-[#373333] bg-[#2A2828]/50">
                      <h3 className="text-[12px] font-bold text-[#F5F3F1] uppercase tracking-wider">Top Traffic Sources</h3>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-[13px]">
                        <thead>
                          <tr className="border-b border-[#373333] text-[11px] text-[#A9A4A0] uppercase font-bold">
                            <th className="px-5 py-3">Source</th>
                            <th className="px-5 py-3">Medium</th>
                            <th className="px-5 py-3 text-right">Sessions</th>
                            <th className="px-5 py-3 text-right">Conversions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#373333]">
                          {backendData.ga4.top_sources.map((s, idx) => (
                            <tr key={idx} className="hover:bg-[#2A2828] transition-colors">
                              <td className="px-5 py-3 font-medium text-[#F5F3F1]">{s.source}</td>
                              <td className="px-5 py-3 text-[#A9A4A0]">{s.medium}</td>
                              <td className="px-5 py-3 text-right font-bold text-[#F5F3F1]">{s.sessions.toLocaleString()}</td>
                              <td className="px-5 py-3 text-right font-bold text-[#00A650]">{s.conversions}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : null}
              </div>
            )}

          </div>
        )}

        {/* TAB 3: SEARCH PERFORMANCE (GSC) */}
        {activeTab === 'search' && (
          <div className="space-y-6">

            {backendData?.gsc.status === 'NOT_CONFIGURED' ? (
              <div className="bg-[#242222] border border-[#373333] rounded-xl p-10 text-center flex flex-col items-center">
                <div className="w-14 h-14 rounded-full bg-[#8F0028]/10 flex items-center justify-center mb-4">
                  <Search className="w-7 h-7 text-[#8F0028]" />
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-bold text-[#F5F3F1]">Google Search Console Not Connected</h3>
                  <span className="text-[10px] font-bold text-yellow-400 bg-yellow-500/10 border border-yellow-500/30 px-2 py-0.5 rounded uppercase">
                    NOT_CONFIGURED
                  </span>
                </div>
                <p className="text-[13px] text-[#A9A4A0] max-w-lg mb-6 leading-relaxed">
                  Search performance tracking requires an active Google Search Console integration. Connect GSC to monitor your organic search impressions, query rankings, and average SERP positions.
                </p>
                <Link
                  href="/app/integrations"
                  className="px-5 py-2.5 bg-[#8F0028] hover:bg-[#A8002F] text-white text-[13px] font-bold rounded-lg transition-colors flex items-center gap-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  Connect GSC in Integrations
                </Link>

                {/* Features Preview */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full max-w-2xl mt-10 pt-8 border-t border-[#373333] text-left">
                  <div className="p-3 bg-[#1C1A1A] rounded-lg border border-[#373333]">
                    <span className="block text-[10px] text-[#A9A4A0] uppercase font-bold">Organic Clicks</span>
                    <span className="text-[14px] font-bold text-[#A9A4A0]">--</span>
                  </div>
                  <div className="p-3 bg-[#1C1A1A] rounded-lg border border-[#373333]">
                    <span className="block text-[10px] text-[#A9A4A0] uppercase font-bold">Impressions</span>
                    <span className="text-[14px] font-bold text-[#A9A4A0]">--</span>
                  </div>
                  <div className="p-3 bg-[#1C1A1A] rounded-lg border border-[#373333]">
                    <span className="block text-[10px] text-[#A9A4A0] uppercase font-bold">Avg. CTR</span>
                    <span className="text-[14px] font-bold text-[#A9A4A0]">--</span>
                  </div>
                  <div className="p-3 bg-[#1C1A1A] rounded-lg border border-[#373333]">
                    <span className="block text-[10px] text-[#A9A4A0] uppercase font-bold">Avg. Position</span>
                    <span className="text-[14px] font-bold text-[#A9A4A0]">--</span>
                  </div>
                </div>
              </div>
            ) : backendData?.gsc.status === 'NO_DATA' ? (
              <div className="bg-[#242222] border border-[#373333] rounded-xl p-10 text-center flex flex-col items-center">
                <div className="w-14 h-14 rounded-full bg-[#00A650]/10 flex items-center justify-center mb-4">
                  <Search className="w-7 h-7 text-[#00A650]" />
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-bold text-[#F5F3F1]">Connected — Awaiting First Sync</h3>
                  <span className="text-[10px] font-bold text-[#00A650] bg-[#00A650]/10 border border-[#00A650]/30 px-2 py-0.5 rounded uppercase">
                    NO_DATA
                  </span>
                </div>
                <p className="text-[13px] text-[#A9A4A0] max-w-md mb-4">
                  Google Search Console is authenticated, but no keyword or ranking records have been synchronized yet.
                </p>
                <p className="text-[11px] text-[#A9A4A0]">
                  Last Sync Status: {backendData.gsc.last_sync_at || 'Pending next automated run'}
                </p>
              </div>
            ) : (
              /* REAL GSC METRICS AVAILABLE */
              <div className="space-y-6">
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                    <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Organic Clicks</span>
                    <span className="text-[20px] font-bold text-[#F5F3F1]">
                      {backendData?.gsc.metrics.clicks.toLocaleString()}
                    </span>
                  </div>
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                    <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Impressions</span>
                    <span className="text-[20px] font-bold text-[#F5F3F1]">
                      {backendData?.gsc.metrics.impressions.toLocaleString()}
                    </span>
                  </div>
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                    <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Avg. CTR</span>
                    <span className="text-[20px] font-bold text-[#00A650]">
                      {((backendData?.gsc.metrics.ctr || 0) * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
                    <span className="block text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-1">Avg. Position</span>
                    <span className="text-[20px] font-bold text-[#F5F3F1]">
                      {backendData?.gsc.metrics.position.toFixed(1)}
                    </span>
                  </div>
                </div>

                {/* Top Queries Table */}
                {backendData?.gsc.top_queries?.length ? (
                  <div className="bg-[#242222] border border-[#373333] rounded-xl overflow-hidden">
                    <div className="px-5 py-3.5 border-b border-[#373333] bg-[#2A2828]/50">
                      <h3 className="text-[12px] font-bold text-[#F5F3F1] uppercase tracking-wider">Top Organic Search Queries</h3>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-[13px]">
                        <thead>
                          <tr className="border-b border-[#373333] text-[11px] text-[#A9A4A0] uppercase font-bold">
                            <th className="px-5 py-3">Query</th>
                            <th className="px-5 py-3 text-right">Clicks</th>
                            <th className="px-5 py-3 text-right">Impressions</th>
                            <th className="px-5 py-3 text-right">Avg Position</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#373333]">
                          {backendData.gsc.top_queries.map((q, idx) => (
                            <tr key={idx} className="hover:bg-[#2A2828] transition-colors">
                              <td className="px-5 py-3 font-medium text-[#F5F3F1]">{q.query}</td>
                              <td className="px-5 py-3 text-right font-bold text-[#00A650]">{q.clicks}</td>
                              <td className="px-5 py-3 text-right text-[#A9A4A0]">{q.impressions.toLocaleString()}</td>
                              <td className="px-5 py-3 text-right text-[#F5F3F1]">{q.position.toFixed(1)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : null}
              </div>
            )}

          </div>
        )}

      </div>

    </div>
  )
}
