"use client"
import { useState, useEffect } from 'react'
import { useAuth, useDashboard, useOrchestrator, useBrandBrain, useAgents } from '@/lib/providers/MockProvider'
import { 
  Layers, ChevronLeft, ChevronDown, BarChart2, Link as LinkIcon, 
  Globe, FileText, Bot, Search, AlertCircle, ArrowRight, Zap, 
  Target, LineChart, FileCode, Send, Paperclip, CheckCircle2,
  Lock, Plus, Settings, MessageSquare, Briefcase, User, Sparkles
} from 'lucide-react'

import { BusinessOverviewPanel } from '@/components/dashboard/context/BusinessOverviewPanel'
import { WebsiteAnalysisPanel } from '@/components/dashboard/context/WebsiteAnalysisPanel'
import { DocumentsPanel } from '@/components/dashboard/context/DocumentsPanel'
import { AudiencePanel } from '@/components/dashboard/context/AudiencePanel'
import { BrandVoicePanel } from '@/components/dashboard/context/BrandVoicePanel'
import { ProductsPanel } from '@/components/dashboard/context/ProductsPanel'
import { CompetitorsPanel } from '@/components/dashboard/context/CompetitorsPanel'
import { useWebsiteAnalysis } from '@/lib/providers/WebsiteAnalysisProvider'

export default function AIWorkspace() {
  const auth = useAuth()
  const { activeWorkspace, activeBrand } = auth
  const dashboardProvider = useDashboard()
  const orchestratorProvider = useOrchestrator()
  const { analysis } = useWebsiteAnalysis()
  const { brandBrain } = useBrandBrain()
  const agentsProvider = useAgents()
  
  const [agentRuns, setAgentRuns] = useState<any[]>([])
  const [agentsList, setAgentsList] = useState<any[]>([])
  
  const [activeNav, setActiveNav] = useState('Analytics')
  const [dataModel, setDataModel] = useState<any>(null)
  const [analyticsTab, setAnalyticsTab] = useState('SEO')
  const [cmoTab, setCmoTab] = useState('Chat')
  const [cwvDevice, setCwvDevice] = useState<'desktop' | 'mobile'>('desktop')
  const [onboardingData, setOnboardingData] = useState<any>(null)
  const isApi = process.env.NEXT_PUBLIC_DATA_MODE === 'api'

  const competitorsList = isApi 
    ? (brandBrain?.competitors || []).map((c: any) => c.name)
    : (onboardingData?.competitors?.length > 0 ? onboardingData.competitors : ['HubSpot', 'Zoho', 'Freshworks', 'Hootsuite'])

  useEffect(() => {
    try {
      const data = localStorage.getItem('onboardingData')
      if (data) {
        setOnboardingData(JSON.parse(data))
      }
    } catch (e) {}

    async function load() {
      try {
        const data = await dashboardProvider.getDashboard()
        setDataModel(data)
        
        if (isApi) {
          try {
            const [runs, agents] = await Promise.all([
              agentsProvider.getAgentRuns(),
              agentsProvider.getAgents()
            ])
            setAgentRuns(runs || [])
            setAgentsList(agents || [])
          } catch(e) { console.error('Failed to load agent runs', e) }
        }
      } catch(e) {}
    }
    load()
  }, [auth.activeBrand?.id])

  return (
    <div className="flex w-full h-full divide-x divide-[#373333]">
      
      {/* ========================================================= */}
      {/* COLUMN 1: CONTEXT */}
      {/* ========================================================= */}
      <div className="w-[260px] lg:w-[280px] shrink-0 flex flex-col h-full bg-[#1C1A1A] overflow-y-auto custom-scrollbar">
        {/* Header */}
        <div className="px-4 py-3 flex items-center justify-between border-b border-[#373333] sticky top-0 bg-[#1C1A1A] z-10">
          <div className="flex items-center gap-2 text-[#F5F3F1] font-bold text-[13px]">
            <Layers className="w-4 h-4 text-[#A9A4A0]" />
            Context
          </div>
          <button className="text-[#A9A4A0] hover:text-[#F5F3F1] transition-colors">
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 space-y-6">
          {/* Workspace Card */}
          <div className="bg-[#242222] border border-[#373333] rounded-xl p-3 flex items-center gap-3 relative group hover:border-[#8F0028]/50 transition-colors cursor-pointer">
            <div className="h-10 w-10 bg-white rounded-lg flex items-center justify-center shrink-0 shadow-sm overflow-hidden">
               {/* StandBharat red icon placeholder */}
               <div className="w-5 h-5 bg-[#8F0028] rounded-[4px] flex items-center justify-center font-bold text-[10px] text-white">
                 {activeBrand?.name?.[0]?.toUpperCase() || 'S'}
               </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[14px] font-bold text-[#F5F3F1] truncate">{activeBrand?.name || 'Brand'}</p>
              <p className="text-[11px] text-[#A9A4A0] truncate">{activeBrand?.category || 'business'} • {activeBrand?.website_url?.replace(/^https?:\/\//,'') || 'website'}</p>
            </div>
            <button className="text-[#A9A4A0] opacity-0 group-hover:opacity-100 hover:text-[#F5F3F1] transition-all absolute right-2 top-2">
              <Settings className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Navigation - Business */}
          <div className="space-y-1">
            <div 
              onClick={() => setActiveNav('Business Overview')}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                activeNav === 'Business Overview' ? 'bg-[#2A2828] text-[#F5F3F1] border-l-2 border-[#8F0028]' : 'text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]'
              }`}
            >
              <Briefcase className={`w-4 h-4 ${activeNav === 'Business Overview' ? 'text-[#8F0028]' : ''}`} />
              <span className="text-[13px] font-semibold">Business Overview</span>
            </div>
            <div 
              onClick={() => setActiveNav('Website Analysis')}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                activeNav === 'Website Analysis' ? 'bg-[#2A2828] text-[#F5F3F1] border-l-2 border-[#8F0028]' : 'text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]'
              }`}
            >
              <Globe className="w-4 h-4" />
              <span className="text-[13px] font-medium">Website Analysis</span>
            </div>
            <div 
              onClick={() => setActiveNav('Audience')}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                activeNav === 'Audience' ? 'bg-[#2A2828] text-[#F5F3F1] border-l-2 border-[#8F0028]' : 'text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]'
              }`}
            >
              <User className={`w-4 h-4 ${activeNav === 'Audience' ? 'text-[#8F0028]' : ''}`} />
              <span className="text-[13px] font-medium">Audience</span>
            </div>
            <div 
              onClick={() => setActiveNav('Brand Voice')}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                activeNav === 'Brand Voice' ? 'bg-[#2A2828] text-[#F5F3F1] border-l-2 border-[#8F0028]' : 'text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]'
              }`}
            >
              <MessageSquare className={`w-4 h-4 ${activeNav === 'Brand Voice' ? 'text-[#8F0028]' : ''}`} />
              <span className="text-[13px] font-medium">Brand Voice</span>
            </div>
            <div 
              onClick={() => setActiveNav('Products & Services')}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                activeNav === 'Products & Services' ? 'bg-[#2A2828] text-[#F5F3F1] border-l-2 border-[#8F0028]' : 'text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]'
              }`}
            >
              <Target className={`w-4 h-4 ${activeNav === 'Products & Services' ? 'text-[#8F0028]' : ''}`} />
              <span className="text-[13px] font-medium">Products & Services</span>
            </div>
          </div>

          {/* Navigation - Documents */}
          <div className="space-y-2 pt-2">
            <div className="flex items-center justify-between px-3 mb-2">
              <span className="text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider">Knowledge Base</span>
              <button 
                onClick={() => setActiveNav('Documents')}
                className="text-[#A9A4A0] hover:text-[#F5F3F1]"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>
            
            <div 
              onClick={() => setActiveNav('Documents')}
              className={`flex items-center justify-between px-3 py-1.5 rounded-lg cursor-pointer transition-colors ${
                activeNav === 'Documents' ? 'bg-[#2A2828] text-[#F5F3F1] border-l-2 border-[#8F0028]' : 'text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]'
              }`}
            >
              <div className="flex items-center gap-2">
                <FileText className={`w-3.5 h-3.5 ${activeNav === 'Documents' ? 'text-[#8F0028]' : ''}`} />
                <span className="text-[13px] font-medium">All Documents</span>
              </div>
            </div>
            
            {['Product Information', 'Marketing Strategy', 'Brand Voice Guide'].map(doc => (
              <div 
                key={doc} 
                onClick={() => setActiveNav(doc)}
                className={`flex items-center justify-between px-3 py-1.5 cursor-pointer transition-colors ${
                  activeNav === doc ? 'text-[#F5F3F1] bg-[#2A2828] rounded-lg' : 'text-[#A9A4A0] hover:text-[#F5F3F1]'
                }`}
              >
                <div className="flex items-center gap-2">
                  <FileText className={`w-3.5 h-3.5 ${activeNav === doc ? 'text-[#8F0028]' : ''}`} />
                  <span className="text-[13px] font-medium">{doc}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Navigation - Competitors */}
          <div className="space-y-2 pt-2">
            <div className="flex items-center justify-between px-3 mb-2">
              <span className="text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider">Competitors</span>
              <button className="text-[#A9A4A0] hover:text-[#F5F3F1]"><Plus className="w-3.5 h-3.5" /></button>
            </div>
            
            {competitorsList.map((comp: string) => (
              <div 
                key={comp} 
                onClick={() => setActiveNav(comp)}
                className={`flex items-center justify-between px-3 py-1.5 group cursor-pointer transition-colors ${
                  activeNav === comp ? 'text-[#F5F3F1] bg-[#2A2828] rounded-lg' : 'text-[#A9A4A0] hover:text-[#F5F3F1]'
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className={`w-4 h-4 rounded flex items-center justify-center text-[9px] font-bold text-white uppercase ${activeNav === comp ? 'bg-[#8F0028]' : 'bg-[#373333]'}`}>{comp.charAt(0)}</div>
                  <span className="text-[13px] font-medium">{comp}</span>
                </div>
              </div>
            ))}
          </div>
          
          <div className="pt-4 pb-8 px-3">
             <p className="text-[11px] text-[#A9A4A0] italic">"What your CMO reads before writing anything."</p>
          </div>
        </div>
      </div>


      {/* ========================================================= */}
      {/* COLUMN 2: MIDDLE PANE (ANALYTICS OR CONTEXT) */}
      {/* ========================================================= */}
      <div className="flex-1 min-w-[400px] flex flex-col h-full bg-[#1C1A1A] overflow-hidden">
        
        {activeNav === 'Business Overview' ? (
          <BusinessOverviewPanel />
        ) : activeNav === 'Website Analysis' ? (
          <WebsiteAnalysisPanel />
        ) : activeNav === 'Documents' ? (
          <DocumentsPanel />
        ) : activeNav === 'Audience' ? (
          <AudiencePanel />
        ) : activeNav === 'Brand Voice' ? (
          <BrandVoicePanel />
        ) : activeNav === 'Products & Services' ? (
          <ProductsPanel />
        ) : activeNav === 'Competitors' || competitorsList.includes(activeNav) ? (
          <CompetitorsPanel />
        ) : activeNav !== 'Analytics' ? (
          <div className="flex-1 flex flex-col h-full bg-[#1C1A1A] p-8 overflow-y-auto custom-scrollbar">
             <div className="mb-6">
               <h2 className="text-[20px] font-bold text-[#F5F3F1] mb-1">{activeNav}</h2>
               <p className="text-[13px] text-[#A9A4A0]">
                 {activeNav === 'Audience' ? 'Define who you are targeting and their core pain points.' :
                  activeNav === 'Brand Voice' ? 'Configure the tone, language, and guidelines for your brand.' :
                  activeNav === 'Products & Services' ? 'Manage your catalog of offerings and their unique selling propositions.' :
                  'View and manage this document from your Knowledge Base.'}
               </p>
             </div>
             
             {/* Documents/Strategy Files Fallback */}
             {(['Product Information', 'Marketing Strategy', 'Brand Voice Guide'].includes(activeNav)) && (
               <div className="bg-[#242222] border border-[#373333] rounded-xl overflow-hidden flex flex-col min-h-[400px]">
                 <div className="px-5 py-3 border-b border-[#373333] flex items-center justify-between bg-[#1C1A1A]">
                   <div className="flex items-center gap-2 text-[13px] font-bold text-white">
                     <FileText className="w-4 h-4 text-[#8F0028]" />
                     {activeNav}.pdf
                   </div>
                   <div className="text-[11px] font-medium text-[#00A650] bg-[#00A650]/10 px-2 py-1 rounded flex items-center gap-1">
                     <CheckCircle2 className="w-3 h-3" /> Indexed for AI
                   </div>
                 </div>
                 <div className="flex-1 p-6 bg-[#242222]">
                   <div className="max-w-2xl">
                     <h3 className="text-lg font-bold text-white mb-4">{activeNav} Overview</h3>
                     <div className="space-y-4 text-[13px] text-[#A9A4A0] leading-relaxed">
                       <p>This document contains the foundational knowledge for {activeNav.toLowerCase()}. It was successfully processed and vectorized into the Knowledge Base.</p>
                       <div className="bg-[#1C1A1A] p-4 rounded border border-[#373333]">
                         <span className="font-bold text-white block mb-2">Key Extracted Entities:</span>
                         <ul className="list-disc pl-4 space-y-1">
                           {activeNav === 'Marketing Strategy' ? (
                             <><li className="ml-2">Q4 Revenue Goals: $1.2M</li><li className="ml-2">Primary Channel: Organic LinkedIn</li><li className="ml-2">Target CAC: &lt;$150</li></>
                           ) : activeNav === 'Product Information' ? (
                             <><li className="ml-2">Core Features: Automated workflows, agent routing, real-time analytics</li><li className="ml-2">Pricing Tiers: Basic, Pro, Enterprise</li></>
                           ) : (
                             <><li className="ml-2">Brand Archetype: The Sage</li><li className="ml-2">Forbidden Words: "Cheap", "Hack", "Magic"</li><li className="ml-2">Sentence Structure: Short, active voice</li></>
                           )}
                         </ul>
                       </div>
                       <p>AI Agents are currently using this context when generating content and routing tasks.</p>
                     </div>
                   </div>
                 </div>
               </div>
             )}
          </div>
        ) : (
          <>
            {/* Analytics Header */}
            <div className="px-6 py-3 flex items-center justify-between border-b border-[#373333] shrink-0 bg-[#1C1A1A]">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-[#F5F3F1] font-bold text-[13px]">
                  <BarChart2 className="w-4 h-4 text-[#A9A4A0]" />
                  Analytics
                </div>
                <div className="h-1.5 w-1.5 rounded-full bg-[#00A650]"></div>
              </div>
          
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-[#242222] border border-[#373333] rounded-md text-[11px] font-medium text-[#A9A4A0] cursor-pointer hover:text-[#F5F3F1]">
              Last 30 days <ChevronDown className="w-3 h-3" />
            </div>
            <button className="text-[#A9A4A0] hover:text-[#F5F3F1]">
              <LinkIcon className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center px-6 border-b border-[#373333] shrink-0">
           {['SEO', 'Links', 'GEO', 'Content'].map(tab => (
             <button 
               key={tab}
               onClick={() => setAnalyticsTab(tab)}
               className={`px-5 py-3 text-[13px] font-semibold border-b-2 transition-colors ${
                 analyticsTab === tab ? 'border-[#8F0028] text-[#F5F3F1]' : 'border-transparent text-[#A9A4A0] hover:text-[#F5F3F1]'
               }`}
             >
               {tab}
             </button>
           ))}
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-10">
          
          {analyticsTab === 'SEO' && (
            isApi ? (
              <div className="flex flex-col items-center justify-center py-20 opacity-50">
                 <BarChart2 className="w-12 h-12 text-[#A9A4A0] mb-4" />
                 <p className="text-[#F5F3F1] font-bold text-lg">NO_DATA</p>
                 <p className="text-[#A9A4A0] text-[13px] mt-1">Analytics integration is not configured.</p>
              </div>
            ) : (
            <>
              {/* Connect Google Services */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider">Connect Google Services</h3>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  {/* Google Analytics */}
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-5 hover:border-[#4A4545] transition-colors">
                    <div className="flex items-start gap-3 mb-4">
                      <div className="w-8 h-8 rounded bg-orange-500/10 flex items-center justify-center shrink-0">
                         <BarChart2 className="w-4 h-4 text-orange-500" />
                      </div>
                      <div>
                        <h4 className="text-[14px] font-bold text-[#F5F3F1]">Google Analytics</h4>
                        <p className="text-[11px] text-[#A9A4A0] mt-0.5">Traffic & behavior</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-[#00A650]"></div>
                      <span className="text-[12px] font-medium text-[#00A650]">Connected</span>
                    </div>
                    <p className="text-[11px] text-[#A9A4A0] mb-4">Last synced 12m ago</p>
                    <button className="w-full py-2 bg-[#2E2B2B] hover:bg-[#373333] text-[#F5F3F1] text-[12px] font-bold rounded-lg transition-colors border border-[#373333]">
                      View Data
                    </button>
                  </div>

                  {/* Search Console */}
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-5 hover:border-[#4A4545] transition-colors">
                    <div className="flex items-start gap-3 mb-4">
                      <div className="w-8 h-8 rounded bg-blue-500/10 flex items-center justify-center shrink-0">
                         <Search className="w-4 h-4 text-blue-500" />
                      </div>
                      <div>
                        <h4 className="text-[14px] font-bold text-[#F5F3F1]">Search Console</h4>
                        <p className="text-[11px] text-[#A9A4A0] mt-0.5">Search rankings</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-[#00A650]"></div>
                      <span className="text-[12px] font-medium text-[#00A650]">Connected</span>
                    </div>
                    <p className="text-[11px] text-[#A9A4A0] mb-4">Last synced 18m ago</p>
                    <button className="w-full py-2 bg-[#2E2B2B] hover:bg-[#373333] text-[#F5F3F1] text-[12px] font-bold rounded-lg transition-colors border border-[#373333]">
                      View Data
                    </button>
                  </div>
                </div>
              </div>

              {/* PageSpeed Scores */}
              <div className="space-y-4">
                <div className="flex items-end justify-between">
                  <div>
                    <h3 className="text-[16px] font-bold text-[#F5F3F1]">PageSpeed Scores</h3>
                    <p className="text-[12px] text-[#A9A4A0] mt-1">Lighthouse scores from Google</p>
                  </div>
                  <span className="text-[11px] text-[#A9A4A0]">Last audited: 2 hours ago</span>
                </div>
                
                <div className="flex flex-col gap-4">
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
                    <h4 className="text-[11px] font-bold text-[#F5F3F1] uppercase tracking-wider mb-5">Mobile</h4>
                    <div className="flex justify-between px-1">
                       {[{score: 56, label: 'Performance', color: '#F59E0B'}, {score: 85, label: 'Accessibility', color: '#F59E0B'}, {score: 100, label: 'Best Practices', color: '#00A650'}, {score: 91, label: 'SEO', color: '#00A650'}].map(s => (
                         <div key={s.label} className="flex flex-col items-center gap-2 flex-1 px-1">
                           <div className="w-12 h-12 rounded-full border-[3px] flex items-center justify-center shrink-0" style={{ borderColor: s.color }}>
                             <span className="text-[14px] font-bold text-[#F5F3F1]">{s.score}</span>
                           </div>
                           <span className="text-[8px] text-[#A9A4A0] uppercase tracking-widest text-center leading-tight break-words max-w-[50px]">{s.label}</span>
                         </div>
                       ))}
                    </div>
                  </div>
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
                    <h4 className="text-[11px] font-bold text-[#F5F3F1] uppercase tracking-wider mb-5">Desktop</h4>
                    <div className="flex justify-between px-1">
                       {[{score: 96, label: 'Performance', color: '#00A650'}, {score: 85, label: 'Accessibility', color: '#F59E0B'}, {score: 100, label: 'Best Practices', color: '#00A650'}, {score: 91, label: 'SEO', color: '#00A650'}].map(s => (
                         <div key={s.label} className="flex flex-col items-center gap-2 flex-1 px-1">
                           <div className="w-12 h-12 rounded-full border-[3px] flex items-center justify-center shrink-0" style={{ borderColor: s.color }}>
                             <span className="text-[14px] font-bold text-[#F5F3F1]">{s.score}</span>
                           </div>
                           <span className="text-[8px] text-[#A9A4A0] uppercase tracking-widest text-center leading-tight break-words max-w-[50px]">{s.label}</span>
                         </div>
                       ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Core Web Vitals & SEO Health row */}
              <div className="grid grid-cols-2 gap-4">
                
                {/* Core Web Vitals */}
                <div className="space-y-4">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <h3 className="text-[16px] font-bold text-[#F5F3F1]">Core Web Vitals</h3>
                      <p className="text-[12px] text-[#A9A4A0] mt-1 truncate">Real user metrics from Chrome UX Report</p>
                    </div>
                    <div className="flex bg-[#242222] border border-[#373333] rounded-md overflow-hidden shrink-0">
                      <button 
                        onClick={() => setCwvDevice('desktop')}
                        className={`px-3 py-1 text-[11px] font-bold ${cwvDevice === 'desktop' ? 'bg-[#8F0028] text-white' : 'text-[#A9A4A0] hover:text-[#F5F3F1]'}`}
                      >Desktop</button>
                      <button 
                        onClick={() => setCwvDevice('mobile')}
                        className={`px-3 py-1 text-[11px] font-bold ${cwvDevice === 'mobile' ? 'bg-[#8F0028] text-white' : 'text-[#A9A4A0] hover:text-[#F5F3F1]'}`}
                      >Mobile</button>
                    </div>
                  </div>
                  
                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-5 grid grid-cols-2 gap-y-6">
                    <div>
                      <div className="flex items-center gap-1.5 mb-1 text-[11px] font-bold text-[#A9A4A0] uppercase"><div className="w-1.5 h-1.5 rounded-full bg-[#00A650]"></div> LCP</div>
                      <div className="text-[20px] font-bold text-[#F5F3F1]">{cwvDevice === 'desktop' ? '0.8s' : '1.3s'}</div>
                      <div className="text-[12px] font-medium text-[#00A650]">Good</div>
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5 mb-1 text-[11px] font-bold text-[#A9A4A0] uppercase"><div className={`w-1.5 h-1.5 rounded-full ${cwvDevice === 'desktop' ? 'bg-[#00A650]' : 'bg-[#F59E0B]'}`}></div> INP</div>
                      <div className="text-[20px] font-bold text-[#F5F3F1]">{cwvDevice === 'desktop' ? '0.2s' : '0.5s'}</div>
                      <div className={`text-[12px] font-medium ${cwvDevice === 'desktop' ? 'text-[#00A650]' : 'text-[#F59E0B]'}`}>{cwvDevice === 'desktop' ? 'Good' : 'Needs Improvement'}</div>
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5 mb-1 text-[11px] font-bold text-[#A9A4A0] uppercase"><div className="w-1.5 h-1.5 rounded-full bg-[#00A650]"></div> CLS</div>
                      <div className="text-[20px] font-bold text-[#F5F3F1]">0.000</div>
                      <div className="text-[12px] font-medium text-[#00A650]">Good</div>
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5 mb-1 text-[11px] font-bold text-[#A9A4A0] uppercase"><div className="w-1.5 h-1.5 rounded-full bg-[#00A650]"></div> FCP</div>
                      <div className="text-[20px] font-bold text-[#F5F3F1]">{cwvDevice === 'desktop' ? '0.5s' : '0.8s'}</div>
                      <div className="text-[12px] font-medium text-[#00A650]">Good</div>
                    </div>
                  </div>
                </div>

                {/* SEO Health */}
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-[16px] font-bold text-[#F5F3F1]">SEO Health</h3>
                      <p className="text-[12px] text-[#A9A4A0] mt-1">On-page metadata and content signals</p>
                    </div>
                    <div className="text-right">
                       <button className="text-[11px] font-bold text-[#8F0028] hover:text-[#F5F3F1] uppercase flex items-center gap-1">
                         View all <ArrowRight className="w-3 h-3" />
                       </button>
                       <div className="mt-2 text-[20px] font-bold text-[#F5F3F1]">
                         {analysis?.result_metadata ? (
                           [
                             analysis.result_metadata.title,
                             analysis.result_metadata.meta_description_exists,
                             analysis.result_metadata.canonical_exists,
                             analysis.result_metadata.h1_exists,
                             analysis.result_metadata.open_graph_exists
                           ].filter(Boolean).length * 20
                         ) : 0} <span className="text-[12px] text-[#A9A4A0]">/ 100</span>
                       </div>
                       <div className="w-full h-1 bg-[#373333] rounded-full mt-1 overflow-hidden">
                         <div className="h-full bg-[#00A650]" style={{ width: `${analysis?.result_metadata ? [analysis.result_metadata.title, analysis.result_metadata.meta_description_exists, analysis.result_metadata.canonical_exists, analysis.result_metadata.h1_exists, analysis.result_metadata.open_graph_exists].filter(Boolean).length * 20 : 0}%` }}></div>
                       </div>
                    </div>
                  </div>

                  <div className="bg-[#242222] border border-[#373333] rounded-xl overflow-hidden divide-y divide-[#373333]">
                     {[
                       { label: 'Meta Title', status: !analysis?.result_metadata ? 'N/A' : (analysis.result_metadata.title ? 'Good' : 'Missing'), color: !analysis?.result_metadata ? 'text-[#A9A4A0]' : (analysis.result_metadata.title ? 'text-[#00A650]' : 'text-[#EF4444]') },
                       { label: 'Meta Description', status: !analysis?.result_metadata ? 'N/A' : (analysis.result_metadata.meta_description_exists ? 'Good' : 'Warning'), color: !analysis?.result_metadata ? 'text-[#A9A4A0]' : (analysis.result_metadata.meta_description_exists ? 'text-[#00A650]' : 'text-[#F59E0B]') },
                       { label: 'Canonical URL', status: !analysis?.result_metadata ? 'N/A' : (analysis.result_metadata.canonical_exists ? 'Good' : 'Warning'), color: !analysis?.result_metadata ? 'text-[#A9A4A0]' : (analysis.result_metadata.canonical_exists ? 'text-[#00A650]' : 'text-[#F59E0B]') },
                       { label: 'H1 Tag', status: !analysis?.result_metadata ? 'N/A' : (analysis.result_metadata.h1_exists ? 'Good' : 'Missing'), color: !analysis?.result_metadata ? 'text-[#A9A4A0]' : (analysis.result_metadata.h1_exists ? 'text-[#00A650]' : 'text-[#EF4444]') },
                       { label: 'Open Graph', status: !analysis?.result_metadata ? 'N/A' : (analysis.result_metadata.open_graph_exists ? 'Good' : 'Missing'), color: !analysis?.result_metadata ? 'text-[#A9A4A0]' : (analysis.result_metadata.open_graph_exists ? 'text-[#00A650]' : 'text-[#EF4444]') },
                     ].map(item => (
                       <div key={item.label} className="px-4 py-2.5 flex items-center justify-between">
                         <span className="text-[13px] font-medium text-[#F5F3F1]">{item.label}</span>
                         <span className={`text-[11px] font-bold ${item.color}`}>{item.status}</span>
                       </div>
                     ))}
                  </div>
                </div>

              </div>
            </>
            )
          )}

          {analyticsTab !== 'SEO' && (
            <div className="flex flex-col items-center justify-center py-20 opacity-50">
               <FileCode className="w-12 h-12 text-[#A9A4A0] mb-4" />
               <p className="text-[#F5F3F1] font-medium">Intelligence data for {analyticsTab} is currently syncing.</p>
               <p className="text-[#A9A4A0] text-[13px] mt-1">AI agents are processing this domain.</p>
            </div>
          )}

        </div>
        </>
        )}
      </div>


      {/* ========================================================= */}
      {/* COLUMN 3: AGENTS FEED */}
      {/* ========================================================= */}
      <div className="w-[300px] lg:w-[320px] shrink-0 flex flex-col h-full bg-[#1C1A1A] border-r border-[#373333] shadow-[4px_0_24px_rgba(0,0,0,0.5)] z-20 overflow-hidden relative">
        <div className="absolute inset-0 bg-gradient-to-b from-[#1C1A1A] to-[#171515] pointer-events-none z-[-1]"></div>
        
        {/* Header */}
        <div className="px-4 py-3 flex items-center justify-between border-b border-[#373333] shrink-0">
          <div className="flex items-center gap-2 text-[#F5F3F1] font-bold text-[13px]">
            <Bot className="w-4 h-4 text-[#A9A4A0]" />
            Agents Feed
            <div className="h-1.5 w-1.5 rounded-full bg-[#00A650] ml-1"></div>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-[#A9A4A0]">
            <Settings className="w-3 h-3" />
            Last updated 2m ago
          </div>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-6">
            <>
              {/* Needs Attention */}
              <div className="space-y-3">
                 <div className="flex items-center justify-between">
                   <h3 className="text-[13px] font-bold text-[#F5F3F1]">Needs Your Attention</h3>
                   <div className="px-1.5 py-0.5 rounded-full bg-[#8F0028] text-white text-[10px] font-bold">3</div>
                 </div>
                 
                 {/* Alert Card */}
                 <div className="bg-[#2A151B] border border-[#8F0028] rounded-xl p-4">
                   <div className="flex items-start gap-3">
                     <div className="w-8 h-8 rounded bg-[#8F0028]/20 flex items-center justify-center shrink-0">
                       <AlertCircle className="w-4 h-4 text-[#FF4560]" />
                     </div>
                     <div className="flex-1 min-w-0">
                       <div className="flex items-center justify-between mb-1">
                         <h4 className="text-[13px] font-bold text-[#F5F3F1]">Content Agent</h4>
                         <span className="text-[10px] text-[#A9A4A0]">2h ago</span>
                       </div>
                       <p className="text-[12px] text-[#F5F3F1] font-medium leading-snug mb-3">3 posts ready for your review</p>
                       
                       <div className="flex gap-2">
                         <button className="flex-1 py-1.5 bg-transparent border border-[#8F0028] text-[#FF4560] text-[11px] font-bold rounded hover:bg-[#8F0028]/10 transition-colors">Review</button>
                         <button className="flex-1 py-1.5 bg-[#8F0028] hover:bg-[#A3002D] text-white text-[11px] font-bold rounded transition-colors shadow-lg shadow-[#8F0028]/20">Approve All</button>
                       </div>
                     </div>
                   </div>
                 </div>
              </div>

              {/* All Agents */}
              <div className="space-y-3">
                 <h3 className="text-[13px] font-bold text-[#F5F3F1]">All Agents</h3>
                 
                 <div className="space-y-2">
                   {(agentsList.length > 0 ? agentsList : [
                     { name: 'SEO Agent', id: 'seo', icon: Globe, status: '2 recommendations ready', time: '12m ago', color: 'text-blue-400' },
                     { name: 'GEO Agent', id: 'geo', icon: Target, status: '2 citation gaps detected', time: '18m ago', color: 'text-emerald-400' },
                     { name: 'Competitor Agent', id: 'competitor', icon: Zap, status: 'Detected new competitor positioning', time: '26m ago', color: 'text-red-400' },
                     { name: 'Content Agent', id: 'writer', icon: FileText, status: '3 drafts ready for review', time: '1h ago', color: 'text-pink-400' },
                     { name: 'LinkedIn Agent', id: 'linkedin', icon: LinkIcon, status: 'Set up your brand voice to get started', time: '2h ago', color: 'text-blue-500' },
                     { name: 'X Agent', id: 'x', icon: MessageSquare, status: '2 ideas ready', time: '3h ago', color: 'text-white' },
                     { name: 'Reddit Agent', id: 'reddit', icon: Search, status: '2 opportunities ready', time: '3h ago', color: 'text-orange-500' },
                     { name: 'Articles Agent', id: 'content_strategy', icon: FileText, status: '1 topic ready', time: '4h ago', color: 'text-purple-400' },
                     { name: 'UGC Videos Agent', id: 'designer', icon: CheckCircle2, status: '1 draft ready', time: '4h ago', color: 'text-orange-400' },
                   ]).map((agent: any, i) => {
                     // For dynamic agents, calculate status and time from agentRuns
                     const agentId = agent.id || agent.agent_id;
                     const latestRun = agentRuns.find((r: any) => r.agent_id === agentId);
                     
                     // Get icon based on name/id if not present
                     let Icon = agent.icon || Bot;
                     if (!agent.icon) {
                       if (agentId === 'seo') Icon = Globe;
                       else if (agentId === 'geo') Icon = Target;
                       else if (agentId === 'competitor' || agentId === 'performance') Icon = Zap;
                       else if (agentId === 'writer' || agentId === 'content_strategy') Icon = FileText;
                       else if (agentId === 'linkedin') Icon = LinkIcon;
                       else if (agentId === 'x') Icon = MessageSquare;
                       else if (agentId === 'reddit') Icon = Search;
                       else if (agentId === 'designer') Icon = CheckCircle2;
                     }
                     
                     // Determine display status
                     let displayStatus = agent.status;
                     let displayTime = agent.time;
                     let color = agent.color || 'text-[#A9A4A0]';
                     
                     if (latestRun) {
                       if (latestRun.status === 'SUCCESS' || latestRun.status === 'COMPLETED') {
                          displayStatus = 'Run completed successfully';
                          color = 'text-emerald-400';
                       } else if (latestRun.status === 'FAILED' || latestRun.status === 'error') {
                          displayStatus = 'Failed to execute';
                          color = 'text-red-400';
                       } else if (latestRun.status === 'NOT_CONFIGURED') {
                          displayStatus = 'Not configured (e.g. missing API keys)';
                          color = 'text-orange-400';
                       } else {
                          displayStatus = `Status: ${latestRun.status}`;
                          color = 'text-blue-400';
                       }
                       displayTime = new Date(latestRun.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                     } else if (agentsList.length > 0) {
                       displayStatus = 'Idle / Ready to run';
                       displayTime = '--';
                     }
                     
                     return (
                     <div key={agentId || i} className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#242222] transition-colors border border-transparent hover:border-[#373333] cursor-pointer group">
                       <div className="w-8 h-8 rounded-full bg-[#242222] border border-[#373333] flex items-center justify-center shrink-0 group-hover:bg-[#1C1A1A]">
                         <Icon className={`w-4 h-4 ${color}`} />
                       </div>
                       <div className="flex-1 min-w-0">
                         <div className="flex items-center justify-between">
                           <h4 className="text-[13px] font-bold text-[#F5F3F1]">{agent.name}</h4>
                           <span className="text-[10px] text-[#A9A4A0]">{displayTime}</span>
                         </div>
                         <p className="text-[11px] text-[#A9A4A0] truncate font-medium mt-0.5">{displayStatus}</p>
                       </div>
                       <div className="hidden group-hover:flex items-center gap-1 shrink-0 bg-[#1C1A1A] border border-[#373333] rounded px-1.5 py-0.5 text-[9px] font-bold text-[#F5F3F1]">
                         Upgrade <ChevronDown className="w-3 h-3" />
                       </div>
                     </div>
                     )
                   })}
                 </div>
              </div>
            </>
        </div>
      </div>

      {/* ========================================================= */}
      {/* COLUMN 4: AI CMO */}
      {/* ========================================================= */}
      <div className="w-[340px] lg:w-[380px] shrink-0 flex flex-col h-full bg-[#1C1A1A]">
        {/* Header */}
        <div className="px-4 py-3 flex items-center justify-between border-b border-[#373333] shrink-0 bg-[#1C1A1A]">
          <div className="flex items-center gap-2 text-[#F5F3F1] font-bold text-[13px]">
            <Sparkles className="w-4 h-4 text-[#8F0028]" />
            AI CMO
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-[#00A650]"></div>
              <span className="text-[11px] font-medium text-[#00A650]">Online</span>
            </div>
            <Settings className="w-3.5 h-3.5 text-[#A9A4A0] hover:text-[#F5F3F1] cursor-pointer" />
          </div>
        </div>

        {/* Identity block */}
        <div className="p-5 flex items-center gap-3 border-b border-[#373333] shrink-0">
          <div className="w-10 h-10 rounded-xl bg-[#8F0028] flex items-center justify-center shrink-0 shadow-lg shadow-[#8F0028]/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-[15px] font-bold text-[#F5F3F1]">{activeBrand?.name || 'Brand'} AI CMO</h2>
            <p className="text-[12px] text-[#A9A4A0] font-medium">Your always-on marketing strategist</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center px-5 border-b border-[#373333] shrink-0">
           {['Chat', 'Research', 'Strategy', 'Tasks'].map(tab => (
             <button 
               key={tab}
               onClick={() => setCmoTab(tab)}
               className={`flex-1 py-3 text-[12px] font-semibold border-b-2 transition-colors text-center ${
                 cmoTab === tab ? 'border-[#8F0028] text-[#F5F3F1]' : 'border-transparent text-[#A9A4A0] hover:text-[#F5F3F1]'
               }`}
             >
               {tab}
             </button>
           ))}
        </div>

        {/* Chat Feed */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-5 flex flex-col gap-4">
          
          {/* AI Message - Insights */}
          <div className="bg-[#242222] border border-[#373333] rounded-2xl rounded-tl-sm p-4 text-[13px] text-[#F5F3F1] leading-relaxed shadow-sm max-w-[95%]">
            <p className="mb-3">Hi, I'm your AI CMO.</p>
            <p className="mb-4 text-[#A9A4A0]">I've analyzed <span className="font-bold text-[#F5F3F1]">{activeBrand?.website_url?.replace(/^https?:\/\//,'') || 'your brand'}</span> and understand your business.</p>
            
            <p className="font-bold mb-3">Here are 3 key insights:</p>
            
            <div className="space-y-3 mb-4">
               <div className="flex items-start gap-3">
                 <div className="w-5 h-5 rounded-full bg-[#8F0028]/20 text-[#FF4560] flex items-center justify-center shrink-0 text-[10px] font-bold mt-0.5">1</div>
                 <p className="text-[12.5px] font-medium">Your website's SEO health is good, but there are 7 on-page issues to fix.</p>
               </div>
               <div className="flex items-start gap-3">
                 <div className="w-5 h-5 rounded-full bg-[#8F0028]/20 text-[#FF4560] flex items-center justify-center shrink-0 text-[10px] font-bold mt-0.5">2</div>
                 <p className="text-[12.5px] font-medium">Competitors are creating content around "AI marketing automation" that you can target.</p>
               </div>
               <div className="flex items-start gap-3">
                 <div className="w-5 h-5 rounded-full bg-[#8F0028]/20 text-[#FF4560] flex items-center justify-center shrink-0 text-[10px] font-bold mt-0.5">3</div>
                 <p className="text-[12.5px] font-medium">LinkedIn is your biggest opportunity based on your current positioning.</p>
               </div>
            </div>

            <p className="text-[#A9A4A0] mb-4">I recommend we publish a 3-part LinkedIn thought-leadership campaign based on your best-performing content themes.</p>
            
            <button className="w-full py-2.5 bg-[#8F0028] hover:bg-[#A3002D] text-white text-[12px] font-bold rounded-xl transition-colors shadow-lg shadow-[#8F0028]/20 flex items-center justify-center gap-2">
              Review my recommendation <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Spacer */}
          <div className="flex-1"></div>

          {/* Suggestions */}
          <div className="space-y-1.5 mt-4">
             <div className="flex items-center justify-between px-2 mb-2">
                <span className="text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider">Suggestions</span>
                <span className="text-[10px] text-[#A9A4A0]">Press ↵ to browse</span>
             </div>
             {[
               { icon: Sparkles, text: "What's my 30 day marketing strategy?" },
               { icon: User, text: "Who's my target customer and what pain points..." },
               { icon: Target, text: "Show me the competitors I'm tracking" },
               { icon: MessageSquare, text: "How do you think we should position our product?" },
               { icon: FileText, text: "Write me a one-liner that sells my product better" },
             ].map((s, i) => (
               <div key={i} className="flex items-center justify-between p-2.5 rounded-xl border border-[#373333] bg-[#1C1A1A] hover:bg-[#242222] transition-colors cursor-pointer group">
                 <div className="flex items-center gap-2.5 min-w-0">
                   <s.icon className="w-3.5 h-3.5 text-[#A9A4A0] shrink-0" />
                   <span className="text-[12px] font-medium text-[#F5F3F1] truncate">{s.text}</span>
                 </div>
                 <ChevronRight className="w-3.5 h-3.5 text-[#A9A4A0] opacity-0 group-hover:opacity-100 shrink-0" />
               </div>
             ))}
          </div>

        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-[#373333] bg-[#1C1A1A] shrink-0">
          <div className="relative bg-[#242222] border border-[#373333] rounded-2xl p-2 pb-10 transition-colors focus-within:border-[#8F0028]">
            <textarea 
              placeholder="Ask me anything..." 
              className="w-full bg-transparent resize-none outline-none text-[13px] text-[#F5F3F1] placeholder:text-[#A9A4A0] p-2 h-[40px] custom-scrollbar"
            />
            
            <div className="absolute bottom-2 left-2 flex items-center gap-1">
              <button className="p-1.5 text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#373333] rounded-lg transition-colors">
                <Paperclip className="w-4 h-4" />
              </button>
              <button className="p-1.5 text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#373333] rounded-lg transition-colors text-[13px] font-bold">
                @
              </button>
              <button className="p-1.5 text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#373333] rounded-lg transition-colors">
                <Globe className="w-4 h-4" />
              </button>
            </div>

            <button className="absolute bottom-2 right-2 p-1.5 bg-[#8F0028] text-white rounded-lg hover:bg-[#A3002D] transition-colors shadow-md shadow-[#8F0028]/20">
              <ArrowUp className="w-4 h-4" />
            </button>
          </div>
        </div>

      </div>

    </div>
  )
}

// Missing inline icons used
const ChevronRight = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" /></svg>
)
const ArrowUp = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg>
)
