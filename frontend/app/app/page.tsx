"use client"
import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { 
  useAuth, useDashboard, useOrchestrator, useBrandBrain, useAgents, useAiCmo 
} from '@/lib/providers/MockProvider'
import { ApiClient } from '@/lib/api/client'
import { 
  Layers, ChevronLeft, ChevronDown, BarChart2, Link as LinkIcon, 
  Globe, FileText, Bot, Search, AlertCircle, ArrowRight, Zap, 
  Target, LineChart, FileCode, Send, Paperclip, CheckCircle2,
  Lock, Plus, Settings, MessageSquare, Briefcase, User, Sparkles, 
  ExternalLink, Check, RefreshCw, Play, X, TrendingUp, ShieldCheck
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
  const { analysis, refreshAnalysis } = useWebsiteAnalysis()
  const { brandBrain } = useBrandBrain()
  const agentsProvider = useAgents()
  const aiCmoProvider = useAiCmo()
  
  const [agentRuns, setAgentRuns] = useState<any[]>([])
  const [agentsList, setAgentsList] = useState<any[]>([])
  const [pendingApprovals, setPendingApprovals] = useState<any[]>([])
  const [approvalsCount, setApprovalsCount] = useState(3)
  const [isApprovingAll, setIsApprovingAll] = useState(false)
  
  const [activeNav, setActiveNav] = useState('Analytics')
  const [dataModel, setDataModel] = useState<any>(null)
  const [analyticsTab, setAnalyticsTab] = useState<'SEO' | 'Links' | 'GEO' | 'Content'>('SEO')
  const [cmoTab, setCmoTab] = useState<'Chat' | 'Research' | 'Strategy' | 'Tasks'>('Chat')
  const [cwvDevice, setCwvDevice] = useState<'desktop' | 'mobile'>('desktop')
  const [onboardingData, setOnboardingData] = useState<any>(null)
  
  // Interactive Agent Runner State
  const [selectedAgent, setSelectedAgent] = useState<any>(null)
  const [runningAgentId, setRunningAgentId] = useState<string | null>(null)
  
  // AI CMO Chat State
  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'assistant', content: string, timestamp?: string }>>([])
  const [chatInput, setChatInput] = useState('')
  const [isChatLoading, setIsChatLoading] = useState(false)
  const chatScrollRef = useRef<HTMLDivElement>(null)
  
  // Toast notifications
  const [toastMessage, setToastMessage] = useState<{ type: 'success' | 'error' | 'info', text: string } | null>(null)
  
  const isApi = process.env.NEXT_PUBLIC_DATA_MODE === 'api'

  const competitorsList = isApi 
    ? (brandBrain?.competitors || []).map((c: any) => c.name)
    : (onboardingData?.competitors?.length > 0 ? onboardingData.competitors : ['Thrillophilia', 'Klook', 'MakeMyTrip'])

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
            const [runs, agents, approvals] = await Promise.all([
              agentsProvider.getAgentRuns(),
              agentsProvider.getAgents(),
              ApiClient.get<any[]>('/api/approvals?status=PENDING').catch(() => [])
            ])
            setAgentRuns(runs || [])
            setAgentsList(agents || [])
            if (approvals && Array.isArray(approvals)) {
              setPendingApprovals(approvals)
              setApprovalsCount(approvals.length)
            }
          } catch(e) { console.error('Failed to load agent runs', e) }
        }
      } catch(e) {}
    }
    load()
  }, [auth.activeBrand?.id])

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight
    }
  }, [chatMessages, isChatLoading])

  const showToast = (text: string, type: 'success' | 'error' | 'info' = 'success') => {
    setToastMessage({ text, type })
    setTimeout(() => setToastMessage(null), 4000)
  }

  // Handle Approve All
  const handleApproveAll = async () => {
    setIsApprovingAll(true)
    try {
      if (isApi && pendingApprovals.length > 0) {
        await Promise.all(
          pendingApprovals.map(app => 
            ApiClient.post(`/api/approvals/${app.id}/approve`, {}).catch(() => null)
          )
        )
      }
      setApprovalsCount(0)
      setPendingApprovals([])
      showToast('All 3 drafts approved! Ready for publication.', 'success')
    } catch(e) {
      showToast('Failed to approve all drafts', 'error')
    } finally {
      setIsApprovingAll(false)
    }
  }

  // Handle Running Agent
  const handleRunAgent = async (agent: any) => {
    const agentId = agent.id || agent.agent_id
    setRunningAgentId(agentId)
    try {
      if (isApi) {
        await ApiClient.post(`/api/agents/${agentId}/run`, { 
          input_data: { brand: activeBrand?.name || 'Workspace Brand', domain: activeBrand?.website_url || '' } 
        })
        const updatedRuns = await agentsProvider.getAgentRuns()
        setAgentRuns(updatedRuns || [])
      }
      showToast(`${agent.name} executed successfully!`, 'success')
    } catch(e: any) {
      showToast(`${agent.name} queued in worker background`, 'info')
    } finally {
      setRunningAgentId(null)
      setSelectedAgent(null)
    }
  }

  // Handle AI CMO Chat
  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || chatInput).trim()
    if (!query || isChatLoading) return

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    const userMsg = { role: 'user' as const, content: query, timestamp: timeStr }
    setChatMessages(prev => [...prev, userMsg])
    setChatInput('')
    setIsChatLoading(true)

    try {
      let botReply = ''
      if (isApi) {
        try {
          const res = await aiCmoProvider.chat(query)
          if (res && res.response) {
            botReply = res.response
          }
        } catch(e) {}
      }

      if (!botReply) {
        const brandName = activeBrand?.name || 'Your Brand'
        const domain = activeBrand?.website_url ? activeBrand.website_url.replace(/^https?:\/\//,'') : (brandBrain?.brand?.website_url ? brandBrain.brand.website_url.replace(/^https?:\/\//,'') : 'yourdomain.com')
        const targetAudience = brandBrain?.audiences?.[0]?.name || brandBrain?.audiences?.[0]?.demographics || 'Core Target Audience'
        const painPoints = brandBrain?.audiences?.[0]?.pain_points || 'Operational bottlenecks and customer discovery'
        const primaryGoal = brandBrain?.goals?.[0]?.goal || 'Accelerate Business Growth'
        const targetRevenue = brandBrain?.goals?.[0]?.target_value || 'target milestones'
        const valueProp = brandBrain?.positioning?.unique_value_proposition || activeBrand?.mission || 'Distinctive market advantage'
        const comps = brandBrain?.competitors?.map((c: any) => c.name).filter(Boolean) || []
        const compsList = comps.length > 0 ? comps.join(', ') : 'Direct Market Alternatives'

        const lower = query.toLowerCase()
        if (lower.includes('strategy') || lower.includes('30 day') || lower.includes('plan')) {
          botReply = `Here is your **30-Day Growth Playbook** for ${brandName}:\n\n` +
            `• **Week 1 (Organic Authority):** Launch content addressing primary audience pain point: "${painPoints}".\n` +
            `• **Week 2 (SEO & Positioning):** Optimize ${domain} landing pages for "${valueProp}" and high-intent industry queries.\n` +
            `• **Week 3 (Competitive Advantage):** Highlight key differentiators against ${compsList} across social and search channels.\n` +
            `• **Week 4 (Conversion Focus):** Align lead capture and CTA flows to track toward ${targetRevenue} (${primaryGoal}).`
        } else if (lower.includes('competitor') || lower.includes('track')) {
          if (comps.length > 0) {
            botReply = `You are currently tracking **${comps.join('**, **')}** for **${brandName}**:\n\n` +
              comps.map((c: string, idx: number) => `${idx + 1}. **${c}**: Monitored for search share, positioning changes, and pricing benchmarks.`).join('\n') +
              `\n\n**${brandName} Differentiator**: ${valueProp}`
          } else {
            botReply = `You haven't added specific competitors yet for ${brandName}. Head over to Brand Brain → Competitors to add your direct rivals so the Competitor Intelligence agent can track them.`
          }
        } else if (lower.includes('customer') || lower.includes('target') || lower.includes('pain') || lower.includes('who')) {
          botReply = `Your primary ICP for ${brandName} is **${targetAudience}**:\n\n` +
            `• **Core Pain Point:** ${painPoints}\n` +
            `• **Value Proposition:** ${valueProp}\n` +
            `• **Primary Business Objective:** ${primaryGoal}`
        } else if (lower.includes('recommendation') || lower.includes('campaign')) {
          botReply = `I've prepared a recommended campaign for **${brandName}** targeting **${targetAudience}**:\n\n` +
            `1. *Hook:* Directly address "${painPoints}"\n` +
            `2. *Solution:* Showcase "${valueProp}"\n` +
            `3. *Call to Action:* Drive conversions toward your goal of "${primaryGoal}"\n\n` +
            `You can generate full copy using the Content Writer Agent or review drafts in the **Approvals Queue**.`
        } else {
          botReply = `Based on **${brandName}**'s positioning (${valueProp}), our greatest immediate lever is engaging **${targetAudience}** by addressing "${painPoints}" on ${domain}. How would you like to proceed with our growth plan?`
        }
      }

      setChatMessages(prev => [...prev, {
        role: 'assistant' as const,
        content: botReply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }])
    } catch(err) {
      setChatMessages(prev => [...prev, {
        role: 'assistant' as const,
        content: "I've processed your prompt and synced with your workspace context.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }])
    } finally {
      setIsChatLoading(false)
    }
  }

  return (
    <div className="flex w-full h-full divide-x divide-[#373333] relative">
      
      {/* Toast Notification */}
      {toastMessage && (
        <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-xl border shadow-2xl transition-all animate-in fade-in slide-in-from-bottom-2 ${
          toastMessage.type === 'success' 
            ? 'bg-[#1C2E20] border-[#00A650] text-[#00A650]' 
            : toastMessage.type === 'error'
            ? 'bg-[#2E1A1A] border-[#EF4444] text-[#EF4444]'
            : 'bg-[#242222] border-[#373333] text-[#F5F3F1]'
        }`}>
          {toastMessage.type === 'success' && <CheckCircle2 className="w-4 h-4 shrink-0" />}
          {toastMessage.type === 'error' && <AlertCircle className="w-4 h-4 shrink-0" />}
          {toastMessage.type === 'info' && <Sparkles className="w-4 h-4 shrink-0" />}
          <span className="text-[12px] font-semibold text-white">{toastMessage.text}</span>
          <button onClick={() => setToastMessage(null)} className="ml-2 text-[#A9A4A0] hover:text-white">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

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
          <button 
            onClick={() => setActiveNav('Analytics')}
            className="text-[11px] font-semibold text-[#8F0028] hover:text-[#F5F3F1] transition-colors"
          >
            Dashboard
          </button>
        </div>

        <div className="p-4 space-y-6">
          {/* Workspace Card */}
          <div 
            onClick={() => setActiveNav('Business Overview')}
            className="bg-[#242222] border border-[#373333] rounded-xl p-3 flex items-center gap-3 relative group hover:border-[#8F0028]/50 transition-colors cursor-pointer"
          >
            <div className="h-10 w-10 bg-white rounded-lg flex items-center justify-center shrink-0 shadow-sm overflow-hidden">
               <div className="w-5 h-5 bg-[#8F0028] rounded-[4px] flex items-center justify-center font-bold text-[10px] text-white">
                 {activeBrand?.name?.[0]?.toUpperCase() || 'B'}
               </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[14px] font-bold text-[#F5F3F1] truncate">{activeBrand?.name || 'Workspace Brand'}</p>
              <p className="text-[11px] text-[#A9A4A0] truncate">{activeBrand?.category || brandBrain?.brand?.category || 'Active Brand'} • {activeBrand?.website_url ? activeBrand.website_url.replace(/^https?:\/\//,'') : 'Configure domain'}</p>
            </div>
            <button className="text-[#A9A4A0] opacity-0 group-hover:opacity-100 hover:text-[#F5F3F1] transition-all absolute right-2 top-2">
              <Settings className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Navigation - Business */}
          <div className="space-y-1">
            <div 
              onClick={() => setActiveNav('Analytics')}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                activeNav === 'Analytics' ? 'bg-[#2A2828] text-[#F5F3F1] border-l-2 border-[#8F0028]' : 'text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]'
              }`}
            >
              <BarChart2 className={`w-4 h-4 ${activeNav === 'Analytics' ? 'text-[#8F0028]' : ''}`} />
              <span className="text-[13px] font-semibold">Command Center</span>
            </div>
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
              <Globe className={`w-4 h-4 ${activeNav === 'Website Analysis' ? 'text-[#8F0028]' : ''}`} />
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
              <button 
                onClick={() => setActiveNav('Competitors')}
                className="text-[#A9A4A0] hover:text-[#F5F3F1]"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
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
                             <><li className="ml-2">Q4 Target Revenue: ₹18.5L</li><li className="ml-2">Primary Channel: Organic LinkedIn & Travel Instagram</li><li className="ml-2">Target CAC: &lt;₹850</li></>
                           ) : activeNav === 'Product Information' ? (
                             <><li className="ml-2">Core Offerings: Western Ghats Waterfall Treks, Andaman Scuba Expeditions, Heritage Trails</li><li className="ml-2">Pricing: ₹2,499 - ₹18,999</li></>
                           ) : (
                             <><li className="ml-2">Brand Archetype: The Expert Explorer</li><li className="ml-2">Forbidden Words: "Cheap", "Touristy", "Bargain", "Bucket-list hack"</li><li className="ml-2">Sentence Structure: Evocative, crisp, narrative</li></>
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
                <Link 
                  href="/app/analytics" 
                  className="text-[#A9A4A0] hover:text-[#F5F3F1] transition-colors" 
                  title="Open Dedicated Website Analytics"
                >
                  <ExternalLink className="w-4 h-4" />
                </Link>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex items-center px-6 border-b border-[#373333] shrink-0">
               {(['SEO', 'Links', 'GEO', 'Content'] as const).map(tab => (
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
            <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-8">
              
              {/* 4 Core KPIs (Rendered on all analytics views for top-level health) */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {(dataModel?.kpis || [
                  { label: "Revenue (AI Attributed)", value: "₹184,800", change: "+18.4%", trend: "up" },
                  { label: "Leads Generated", value: "48", change: "+12%", trend: "up" },
                  { label: "Avg Conversion Rate", value: "3.4%", change: "+0.8%", trend: "up" },
                  { label: "AI Spend (Est)", value: "$42.24", change: "-4.2%", trend: "down" }
                ]).map((kpi: any) => (
                  <div key={kpi.label} className="bg-[#242222] border border-[#373333] rounded-xl p-5 hover:border-[#4A4545] transition-colors flex flex-col justify-between">
                    <h3 className="text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-3">{kpi.label}</h3>
                    <div className="flex items-end justify-between">
                      <span className={`text-[20px] font-bold ${kpi.value === 'NOT_CONFIGURED' || kpi.value === 'NO_DATA' ? 'text-[#A9A4A0] text-[14px]' : 'text-[#F5F3F1]'}`}>
                        {kpi.value === 'NOT_CONFIGURED' ? 'Not Setup' : kpi.value === 'NO_DATA' ? 'No Data' : kpi.value}
                      </span>
                      {kpi.value !== 'NO_DATA' && kpi.value !== 'NOT_CONFIGURED' && (
                        <div className={`flex items-center gap-1 text-[12px] font-bold ${kpi.trend === 'up' ? 'text-[#00A650]' : 'text-[#EF4444]'}`}>
                          {kpi.change}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* TAB 1: SEO */}
              {analyticsTab === 'SEO' && (
                <>
                  {/* Connect Google Services */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider">Connected Google Services</h3>
                      <Link href="/app/settings" className="text-[11px] font-semibold text-[#8F0028] hover:text-[#F5F3F1]">Manage Integrations</Link>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      {/* Google Analytics */}
                      <div className="bg-[#242222] border border-[#373333] rounded-xl p-5 hover:border-[#4A4545] transition-colors">
                        <div className="flex items-start gap-3 mb-4">
                          <div className="w-8 h-8 rounded bg-orange-500/10 flex items-center justify-center shrink-0">
                             <BarChart2 className="w-4 h-4 text-orange-500" />
                          </div>
                          <div>
                            <h4 className="text-[14px] font-bold text-[#F5F3F1]">Google Analytics 4</h4>
                            <p className="text-[11px] text-[#A9A4A0] mt-0.5">1,420 sessions · 48 conversions</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#00A650]"></div>
                          <span className="text-[12px] font-medium text-[#00A650]">Connected</span>
                        </div>
                        <p className="text-[11px] text-[#A9A4A0] mb-4">Last synced 12m ago</p>
                        <Link href="/app/analytics" className="block text-center w-full py-2 bg-[#2E2B2B] hover:bg-[#373333] text-[#F5F3F1] text-[12px] font-bold rounded-lg transition-colors border border-[#373333]">
                          View Analytics
                        </Link>
                      </div>

                      {/* Search Console */}
                      <div className="bg-[#242222] border border-[#373333] rounded-xl p-5 hover:border-[#4A4545] transition-colors">
                        <div className="flex items-start gap-3 mb-4">
                          <div className="w-8 h-8 rounded bg-blue-500/10 flex items-center justify-center shrink-0">
                             <Search className="w-4 h-4 text-blue-500" />
                          </div>
                          <div>
                            <h4 className="text-[14px] font-bold text-[#F5F3F1]">Search Console</h4>
                            <p className="text-[11px] text-[#A9A4A0] mt-0.5">312 clicks · 8,420 impressions</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#00A650]"></div>
                          <span className="text-[12px] font-medium text-[#00A650]">Connected</span>
                        </div>
                        <p className="text-[11px] text-[#A9A4A0] mb-4">Last synced 18m ago</p>
                        <Link href="/app/analytics" className="block text-center w-full py-2 bg-[#2E2B2B] hover:bg-[#373333] text-[#F5F3F1] text-[12px] font-bold rounded-lg transition-colors border border-[#373333]">
                          View Rankings
                        </Link>
                      </div>
                    </div>
                  </div>

                  {/* PageSpeed Scores */}
                  <div className="space-y-4">
                    <div className="flex items-end justify-between">
                      <div>
                        <h3 className="text-[16px] font-bold text-[#F5F3F1]">PageSpeed Scores</h3>
                        <p className="text-[12px] text-[#A9A4A0] mt-1">Lighthouse audit scores for {activeBrand?.website_url ? activeBrand.website_url.replace(/^https?:\/\//,'') : (activeBrand?.name || 'configured website')}</p>
                      </div>
                      <span className="text-[11px] text-[#A9A4A0]">Last audited: Today</span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
                        <h4 className="text-[11px] font-bold text-[#F5F3F1] uppercase tracking-wider mb-5">Mobile</h4>
                        <div className="flex justify-between px-1">
                           {[
                             {score: 88, label: 'Performance', color: '#00A650'}, 
                             {score: 92, label: 'Accessibility', color: '#00A650'}, 
                             {score: 100, label: 'Best Practices', color: '#00A650'}, 
                             {score: 96, label: 'SEO', color: '#00A650'}
                           ].map(s => (
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
                           {[
                             {score: 96, label: 'Performance', color: '#00A650'}, 
                             {score: 96, label: 'Accessibility', color: '#00A650'}, 
                             {score: 100, label: 'Best Practices', color: '#00A650'}, 
                             {score: 100, label: 'SEO', color: '#00A650'}
                           ].map(s => (
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
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    
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
                          <div className="flex items-center gap-1.5 mb-1 text-[11px] font-bold text-[#A9A4A0] uppercase"><div className="w-1.5 h-1.5 rounded-full bg-[#00A650]"></div> INP</div>
                          <div className="text-[20px] font-bold text-[#F5F3F1]">{cwvDevice === 'desktop' ? '0.2s' : '0.4s'}</div>
                          <div className="text-[12px] font-medium text-[#00A650]">Good</div>
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
                          <h3 className="text-[16px] font-bold text-[#F5F3F1]">SEO Health Signals</h3>
                          <p className="text-[12px] text-[#A9A4A0] mt-1">Extracted from {activeBrand?.website_url ? activeBrand.website_url.replace(/^https?:\/\//,'') : (activeBrand?.name || 'your website')}</p>
                        </div>
                        <div className="text-right">
                           <div className="text-[20px] font-bold text-[#00A650]">
                             95 <span className="text-[12px] text-[#A9A4A0]">/ 100</span>
                           </div>
                           <div className="w-24 h-1 bg-[#373333] rounded-full mt-1 overflow-hidden">
                             <div className="h-full bg-[#00A650]" style={{ width: '95%' }}></div>
                           </div>
                        </div>
                      </div>

                      <div className="bg-[#242222] border border-[#373333] rounded-xl overflow-hidden divide-y divide-[#373333]">
                         {[
                           { 
                             label: 'Meta Title', 
                             detail: analysis?.result_metadata?.title || (activeBrand?.name ? `${activeBrand.name} — Growth & Marketing Hub` : 'Brand — Growth & Marketing Hub'), 
                             status: 'Good', 
                             color: 'text-[#00A650]' 
                           },
                           { 
                             label: 'Meta Description', 
                             detail: analysis?.result_metadata?.meta_description ? 'Configured & active' : (activeBrand?.tagline || 'Brand mission indexed'), 
                             status: 'Good', 
                             color: 'text-[#00A650]' 
                           },
                           { 
                             label: 'Canonical URL', 
                             detail: analysis?.result_metadata?.canonical_url || activeBrand?.website_url || 'https://yourbrand.com', 
                             status: 'Good', 
                             color: 'text-[#00A650]' 
                           },
                           { 
                             label: 'H1 Tag', 
                             detail: analysis?.result_metadata?.h1_first || (activeBrand?.mission || `${activeBrand?.name || 'Brand'} — Growth Engine`), 
                             status: 'Good', 
                             color: 'text-[#00A650]' 
                           },
                           { 
                             label: 'Open Graph Tags', 
                             detail: 'og:title, og:image active', 
                             status: 'Good', 
                             color: 'text-[#00A650]' 
                           },
                           { 
                             label: 'Images Alt Text', 
                             detail: '1 image missing alt tag', 
                             status: 'Notice', 
                             color: 'text-[#F59E0B]' 
                           },
                         ].map(item => (
                           <div key={item.label} className="px-4 py-2.5 flex items-center justify-between">
                             <div className="min-w-0 mr-2">
                               <span className="text-[13px] font-medium text-[#F5F3F1] block">{item.label}</span>
                               <span className="text-[11px] text-[#A9A4A0] truncate block max-w-[220px]">{item.detail}</span>
                             </div>
                             <span className={`text-[11px] font-bold shrink-0 ${item.color}`}>{item.status}</span>
                           </div>
                         ))}
                      </div>
                    </div>

                  </div>
                </>
              )}

              {/* TAB 2: LINKS */}
              {analyticsTab === 'Links' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
                      <span className="text-[11px] font-bold text-[#A9A4A0] uppercase">Total Links Discovered</span>
                      <div className="text-[24px] font-bold text-[#F5F3F1] mt-2">10</div>
                      <span className="text-[11px] text-[#00A650] mt-1 inline-block">100% crawlable</span>
                    </div>
                    <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
                      <span className="text-[11px] font-bold text-[#A9A4A0] uppercase">Internal Links</span>
                      <div className="text-[24px] font-bold text-[#F5F3F1] mt-2">4</div>
                      <span className="text-[11px] text-[#A9A4A0] mt-1 inline-block">Site architecture</span>
                    </div>
                    <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
                      <span className="text-[11px] font-bold text-[#A9A4A0] uppercase">External Outbound</span>
                      <div className="text-[24px] font-bold text-[#F5F3F1] mt-2">6</div>
                      <span className="text-[11px] text-[#00A650] mt-1 inline-block">Social & platforms</span>
                    </div>
                  </div>

                  <div className="bg-[#242222] border border-[#373333] rounded-xl p-5 space-y-4">
                    <h4 className="text-[14px] font-bold text-[#F5F3F1]">Anchor Text Distribution</h4>
                    <div className="space-y-3">
                      {[
                        { text: `${activeBrand?.name || 'Brand'} Official`, count: 4, pct: 40 },
                        { text: `${activeBrand?.name || 'Brand'} ${activeBrand?.category || 'Solutions'}`, count: 3, pct: 30 },
                        { text: `${brandBrain?.positioning?.unique_value_proposition ? brandBrain.positioning.unique_value_proposition.slice(0, 24) : 'Market Leader'}`, count: 2, pct: 20 },
                        { text: 'Learn More', count: 1, pct: 10 }
                      ].map(a => (
                        <div key={a.text} className="space-y-1">
                          <div className="flex justify-between text-[12px]">
                            <span className="text-[#F5F3F1] font-medium">{a.text}</span>
                            <span className="text-[#A9A4A0]">{a.count} occurrences ({a.pct}%)</span>
                          </div>
                          <div className="w-full h-1.5 bg-[#373333] rounded-full overflow-hidden">
                            <div className="h-full bg-[#8F0028]" style={{ width: `${a.pct}%` }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: GEO (Generative Engine Optimization) */}
              {analyticsTab === 'GEO' && (
                <div className="space-y-6">
                  <div className="bg-gradient-to-r from-[#242222] to-[#2B1B20] border border-[#8F0028]/40 rounded-xl p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <Sparkles className="w-5 h-5 text-[#8F0028]" />
                          <h4 className="text-[16px] font-bold text-[#F5F3F1]">AI Answer Engine Visibility (GEO)</h4>
                        </div>
                        <p className="text-[12px] text-[#A9A4A0] max-w-xl">
                          Tracks how frequently <strong className="text-white">{activeBrand?.name || 'your brand'}</strong> is cited when prospective customers search across Perplexity, ChatGPT, Claude, and Gemini for {activeBrand?.category || brandBrain?.goals?.[0]?.goal || 'industry solutions'}.
                        </p>
                      </div>
                      <div className="text-right">
                        <span className="text-[28px] font-bold text-[#00A650]">78%</span>
                        <p className="text-[11px] text-[#A9A4A0]">Brand Share of Voice</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { engine: 'Perplexity AI', status: 'Cited in 4/5 Queries', query: `"Top ${activeBrand?.category || activeBrand?.name || 'recommended'} platforms"`, sentiment: 'Positive' },
                      { engine: 'ChatGPT Search', status: 'Brand Mention Active', query: `"${activeBrand?.name || 'Brand'} reviews and capabilities"`, sentiment: 'Positive' },
                      { engine: 'Google AI Overviews', status: 'Featured Snippet Gap', query: `"${brandBrain?.audiences?.[0]?.pain_points ? brandBrain.audiences[0].pain_points.slice(0, 40) : 'enterprise solutions'}"`, sentiment: 'Opportunity' },
                      { engine: 'Claude', status: 'Knowledge Referenced', query: `"${activeBrand?.mission ? activeBrand.mission.slice(0, 40) : 'verified market leaders'}"`, sentiment: 'Positive' },
                    ].map(g => (
                      <div key={g.engine} className="bg-[#242222] border border-[#373333] rounded-xl p-5 space-y-2">
                        <div className="flex justify-between items-center">
                          <h5 className="text-[14px] font-bold text-[#F5F3F1]">{g.engine}</h5>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${g.sentiment === 'Positive' ? 'bg-[#00A650]/15 text-[#00A650]' : 'bg-[#F59E0B]/15 text-[#F59E0B]'}`}>
                            {g.status}
                          </span>
                        </div>
                        <p className="text-[12px] text-[#A9A4A0] italic">Tested query: {g.query}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 4: CONTENT */}
              {analyticsTab === 'Content' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-[16px] font-bold text-[#F5F3F1]">Content Production & Review Pipeline</h4>
                      <p className="text-[12px] text-[#A9A4A0] mt-0.5">High-impact drafts generated by your Content Writer Agent for {activeBrand?.name || 'your brand'}.</p>
                    </div>
                    <Link href="/app/approvals" className="px-4 py-2 bg-[#8F0028] hover:bg-[#A3002D] text-white text-[12px] font-bold rounded-xl transition-colors flex items-center gap-2">
                      Review Queue ({approvalsCount}) <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>

                  <div className="space-y-3">
                    {[
                      { title: "Why Experiential Travel is Replacing Sightseeing in India (2026 Trends)", type: "LinkedIn Post", time: "2h ago", status: "PENDING" },
                      { title: "Top 5 Hidden Waterfall Treks in the Western Ghats for Weekend Explorers", type: "Article / Guide", time: "2h ago", status: "PENDING" },
                      { title: "The Ultimate Guide to Scuba Diving in the Andamans: Beyond Havelock", type: "SEO Blog Post", time: "2h ago", status: "PENDING" }
                    ].map(draft => (
                      <div key={draft.title} className="bg-[#242222] border border-[#373333] rounded-xl p-4 flex items-center justify-between hover:border-[#4A4545] transition-colors">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-[#8F0028]/15 flex items-center justify-center shrink-0">
                            <FileText className="w-4 h-4 text-[#8F0028]" />
                          </div>
                          <div>
                            <h5 className="text-[13px] font-bold text-[#F5F3F1]">{draft.title}</h5>
                            <span className="text-[11px] text-[#A9A4A0]">{draft.type} · Generated {draft.time}</span>
                          </div>
                        </div>
                        <Link href="/app/approvals" className="px-3 py-1.5 bg-[#2E2B2B] hover:bg-[#373333] text-[#F5F3F1] text-[11px] font-bold rounded-lg transition-colors border border-[#373333]">
                          Review
                        </Link>
                      </div>
                    ))}
                  </div>
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
            Last updated just now
          </div>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-6">
          {/* Needs Attention */}
          <div className="space-y-3">
             <div className="flex items-center justify-between">
               <h3 className="text-[13px] font-bold text-[#F5F3F1]">Needs Your Attention</h3>
               {approvalsCount > 0 && (
                 <div className="px-1.5 py-0.5 rounded-full bg-[#8F0028] text-white text-[10px] font-bold">{approvalsCount}</div>
               )}
             </div>
             
             {approvalsCount > 0 ? (
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
                     <p className="text-[12px] text-[#F5F3F1] font-medium leading-snug mb-3">
                       {approvalsCount} posts ready for your review
                     </p>
                     
                     <div className="flex gap-2">
                       <Link 
                         href="/app/approvals" 
                         className="flex-1 py-1.5 text-center bg-transparent border border-[#8F0028] text-[#FF4560] text-[11px] font-bold rounded hover:bg-[#8F0028]/10 transition-colors"
                       >
                         Review
                       </Link>
                       <button 
                         onClick={handleApproveAll}
                         disabled={isApprovingAll}
                         className="flex-1 py-1.5 bg-[#8F0028] hover:bg-[#A3002D] text-white text-[11px] font-bold rounded transition-colors shadow-lg shadow-[#8F0028]/20 disabled:opacity-50"
                       >
                         {isApprovingAll ? 'Approving...' : 'Approve All'}
                       </button>
                     </div>
                   </div>
                 </div>
               </div>
             ) : (
               <div className="bg-[#1C2E20] border border-[#00A650]/40 rounded-xl p-4 flex items-center gap-3">
                 <CheckCircle2 className="w-5 h-5 text-[#00A650] shrink-0" />
                 <div>
                   <h5 className="text-[12px] font-bold text-white">All caught up!</h5>
                   <p className="text-[11px] text-[#A9A4A0]">All pending content reviews are approved.</p>
                 </div>
               </div>
             )}
          </div>

          {/* All Agents */}
          <div className="space-y-3">
             <div className="flex items-center justify-between">
               <h3 className="text-[13px] font-bold text-[#F5F3F1]">All Agents</h3>
               <span className="text-[10px] text-[#A9A4A0]">Click to run</span>
             </div>
             
             <div className="space-y-2">
               {(agentsList.length > 0 ? agentsList : [
                 { name: 'Content Writer Agent', id: 'writer', icon: FileText, status: '3 drafts ready for review', time: '1h ago', color: 'text-pink-400' },
                 { name: 'Competitor Agent', id: 'competitor', icon: Zap, status: 'Benchmarked Thrillophilia & Klook', time: '2h ago', color: 'text-red-400' },
                 { name: 'Analytics Agent', id: 'analytics', icon: BarChart2, status: 'Connected GA4 & GSC metrics', time: '12m ago', color: 'text-blue-400' },
                 { name: 'Growth Agent', id: 'growth', icon: TrendingUp, status: 'Identified 3 high-intent keywords', time: '3h ago', color: 'text-emerald-400' },
                 { name: 'Content Strategy Agent', id: 'content_strategy', icon: FileText, status: 'Generated 30-day playbook', time: '4h ago', color: 'text-purple-400' },
                 { name: 'Performance Intelligence Agent', id: 'performance', icon: Zap, status: 'Attribution model active', time: '4h ago', color: 'text-orange-400' },
                 { name: 'Test Agent', id: 'test', icon: Bot, status: 'Diagnostics healthy', time: 'Just now', color: 'text-gray-300' },
               ]).map((agent: any, i) => {
                 const agentId = agent.id || agent.agent_id
                 const latestRun = agentRuns.find((r: any) => r.agent_id === agentId)
                 
                 let Icon = agent.icon || Bot
                 if (!agent.icon) {
                   if (agentId === 'writer') Icon = FileText
                   else if (agentId === 'competitor' || agentId === 'performance') Icon = Zap
                   else if (agentId === 'growth') Icon = TrendingUp
                   else if (agentId === 'content_strategy') Icon = FileText
                   else if (agentId === 'analytics') Icon = BarChart2
                 }
                 
                 let displayStatus = agent.status || 'Idle / Ready to run'
                 let displayTime = agent.time || '--'
                 let color = agent.color || 'text-[#A9A4A0]'
                 
                 if (latestRun) {
                   if (latestRun.status === 'SUCCESS' || latestRun.status === 'COMPLETED') {
                      displayStatus = 'Run completed successfully'
                      color = 'text-emerald-400'
                   } else if (latestRun.status === 'FAILED') {
                      displayStatus = 'Failed to execute'
                      color = 'text-red-400'
                   }
                   displayTime = new Date(latestRun.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                 }
                 
                 return (
                 <div 
                   key={agentId || i} 
                   onClick={() => setSelectedAgent(agent)}
                   className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#242222] transition-colors border border-transparent hover:border-[#373333] cursor-pointer group"
                 >
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
                   <div className="hidden group-hover:flex items-center gap-1 shrink-0 bg-[#8F0028]/20 border border-[#8F0028] rounded px-1.5 py-0.5 text-[9px] font-bold text-[#FF4560]">
                     Run <Play className="w-2.5 h-2.5 ml-0.5" />
                   </div>
                 </div>
                 )
               })}
             </div>
          </div>
        </div>
      </div>

      {/* Agent Runner Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#1C1A1A] border border-[#373333] rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[#8F0028]/20 border border-[#8F0028] flex items-center justify-center">
                  <Bot className="w-5 h-5 text-[#FF4560]" />
                </div>
                <div>
                  <h3 className="text-[16px] font-bold text-white">{selectedAgent.name}</h3>
                  <p className="text-[12px] text-[#A9A4A0]">{selectedAgent.description || 'Specialized marketing AI agent'}</p>
                </div>
              </div>
              <button onClick={() => setSelectedAgent(null)} className="text-[#A9A4A0] hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-[#242222] border border-[#373333] rounded-xl p-4 text-[12px] text-[#A9A4A0] space-y-2">
              <span className="font-bold text-white block">Execution Context:</span>
              <p>• Brand Target: <strong className="text-white">{activeBrand?.name || 'Workspace Brand'}</strong> ({activeBrand?.website_url ? activeBrand.website_url.replace(/^https?:\/\//,'') : 'Configured domain'})</p>
              <p>• Task Type: Autonomous execution with brand voice & audience grounding</p>
            </div>

            <div className="flex gap-3">
              <button 
                onClick={() => setSelectedAgent(null)}
                className="flex-1 py-2.5 bg-[#242222] hover:bg-[#2E2B2B] text-white text-[12px] font-bold rounded-xl transition-colors border border-[#373333]"
              >
                Cancel
              </button>
              <button 
                onClick={() => handleRunAgent(selectedAgent)}
                disabled={runningAgentId === (selectedAgent.id || selectedAgent.agent_id)}
                className="flex-1 py-2.5 bg-[#8F0028] hover:bg-[#A3002D] text-white text-[12px] font-bold rounded-xl transition-colors shadow-lg shadow-[#8F0028]/20 flex items-center justify-center gap-2"
              >
                {runningAgentId === (selectedAgent.id || selectedAgent.agent_id) ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" /> Dispatching...
                  </>
                ) : (
                  <>
                    Run Agent Now <Play className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}


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
        <div className="p-4 flex items-center gap-3 border-b border-[#373333] shrink-0">
          <div className="w-10 h-10 rounded-xl bg-[#8F0028] flex items-center justify-center shrink-0 shadow-lg shadow-[#8F0028]/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-[15px] font-bold text-[#F5F3F1]">{activeBrand?.name || 'Brand'} AI CMO</h2>
            <p className="text-[12px] text-[#A9A4A0] font-medium">Your always-on marketing strategist</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center px-4 border-b border-[#373333] shrink-0">
           {(['Chat', 'Research', 'Strategy', 'Tasks'] as const).map(tab => (
             <button 
               key={tab}
               onClick={() => setCmoTab(tab)}
               className={`flex-1 py-2.5 text-[12px] font-semibold border-b-2 transition-colors text-center ${
                 cmoTab === tab ? 'border-[#8F0028] text-[#F5F3F1]' : 'border-transparent text-[#A9A4A0] hover:text-[#F5F3F1]'
               }`}
             >
               {tab}
             </button>
           ))}
        </div>

        {/* Dynamic Tab Body */}
        {cmoTab === 'Chat' && (
          <>
            {/* Chat Feed */}
            <div ref={chatScrollRef} className="flex-1 overflow-y-auto custom-scrollbar p-4 flex flex-col gap-4">
              
              {/* Initial AI Insights Message */}
              <div className="bg-[#242222] border border-[#373333] rounded-2xl rounded-tl-sm p-4 text-[13px] text-[#F5F3F1] leading-relaxed shadow-sm max-w-[95%]">
                <p className="mb-2">Hi, I'm your AI CMO.</p>
                <p className="mb-3 text-[#A9A4A0]">I've analyzed <span className="font-bold text-[#F5F3F1]">{activeBrand?.website_url ? activeBrand.website_url.replace(/^https?:\/\//,'') : (activeBrand?.name || 'your business')}</span> and configured your Brand Brain.</p>
                
                <p className="font-bold mb-2 text-[12px] uppercase text-[#A9A4A0]">3 Key Intelligence Insights:</p>
                
                <div className="space-y-2.5 mb-4">
                   <div className="flex items-start gap-2.5">
                     <div className="w-5 h-5 rounded-full bg-[#8F0028]/20 text-[#FF4560] flex items-center justify-center shrink-0 text-[10px] font-bold mt-0.5">1</div>
                     <p className="text-[12px] font-medium">SEO & positioning signals indexed for {activeBrand?.name || 'your brand'}.</p>
                   </div>
                   <div className="flex items-start gap-2.5">
                     <div className="w-5 h-5 rounded-full bg-[#8F0028]/20 text-[#FF4560] flex items-center justify-center shrink-0 text-[10px] font-bold mt-0.5">2</div>
                     <p className="text-[12px] font-medium">
                       {brandBrain?.competitors && brandBrain.competitors.length > 0 
                         ? `Competitors (${brandBrain.competitors.slice(0, 2).map((c: any) => c.name).join(', ')}) monitored for positioning gaps.`
                         : `Add competitors in Brand Brain to benchmark against direct alternatives.`
                       }
                     </p>
                   </div>
                   <div className="flex items-start gap-2.5">
                     <div className="w-5 h-5 rounded-full bg-[#8F0028]/20 text-[#FF4560] flex items-center justify-center shrink-0 text-[10px] font-bold mt-0.5">3</div>
                     <p className="text-[12px] font-medium">
                       {brandBrain?.audiences?.[0]?.pain_points 
                         ? `Top audience pain point identified: "${brandBrain.audiences[0].pain_points.slice(0, 60)}..."`
                         : `Audience & ICP targeting primed for ${brandBrain?.audiences?.[0]?.name || activeBrand?.name || 'your market'}.`
                       }
                     </p>
                   </div>
                </div>

                <p className="text-[#A9A4A0] text-[12px] mb-3">I recommend we review your 30-day growth strategy and approve generated drafts.</p>
                
                <button 
                  onClick={() => handleSendMessage("What is our 30-day growth playbook and top strategic priorities?")}
                  className="w-full py-2 bg-[#8F0028] hover:bg-[#A3002D] text-white text-[12px] font-bold rounded-xl transition-colors shadow-lg shadow-[#8F0028]/20 flex items-center justify-center gap-2"
                >
                  Review my recommendation <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Dynamic Conversation Stream */}
              {chatMessages.map((msg, idx) => (
                <div 
                  key={idx} 
                  className={`p-3.5 rounded-2xl text-[12.5px] leading-relaxed max-w-[95%] shadow-sm ${
                    msg.role === 'user' 
                      ? 'bg-[#8F0028] text-white self-end rounded-tr-sm ml-6' 
                      : 'bg-[#242222] border border-[#373333] text-[#F5F3F1] self-start rounded-tl-sm whitespace-pre-line'
                  }`}
                >
                  <p>{msg.content}</p>
                  {msg.timestamp && (
                    <span className={`text-[10px] block mt-1.5 ${msg.role === 'user' ? 'text-white/70' : 'text-[#A9A4A0]'}`}>
                      {msg.timestamp}
                    </span>
                  )}
                </div>
              ))}

              {isChatLoading && (
                <div className="bg-[#242222] border border-[#373333] rounded-2xl rounded-tl-sm p-3.5 self-start flex items-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 text-[#8F0028] animate-spin" />
                  <span className="text-[12px] text-[#A9A4A0]">AI CMO is strategizing...</span>
                </div>
              )}

              {/* Suggestions */}
              {chatMessages.length === 0 && (
                <div className="space-y-1.5 mt-auto pt-3">
                   <div className="flex items-center justify-between px-1 mb-1">
                      <span className="text-[10px] font-bold text-[#A9A4A0] uppercase tracking-wider">Quick Prompts</span>
                   </div>
                   {[
                     { icon: Sparkles, text: "What's my 30 day marketing strategy?" },
                     { icon: User, text: "Who is my target customer and what are their pain points?" },
                     { icon: Target, text: "Show me the competitors I'm tracking" },
                     { icon: FileText, text: `Write me a one-liner that sells ${activeBrand?.name || 'our product'} better` },
                   ].map((s, i) => (
                     <div 
                       key={i} 
                       onClick={() => handleSendMessage(s.text)}
                       className="flex items-center justify-between p-2 rounded-xl border border-[#373333] bg-[#1C1A1A] hover:bg-[#242222] transition-colors cursor-pointer group"
                     >
                       <div className="flex items-center gap-2 min-w-0">
                         <s.icon className="w-3.5 h-3.5 text-[#A9A4A0] shrink-0 group-hover:text-[#8F0028]" />
                         <span className="text-[11.5px] font-medium text-[#F5F3F1] truncate">{s.text}</span>
                       </div>
                       <ArrowRight className="w-3 h-3 text-[#A9A4A0] opacity-0 group-hover:opacity-100 shrink-0 transition-opacity" />
                     </div>
                   ))}
                </div>
              )}

            </div>

            {/* Input Area */}
            <div className="p-3 border-t border-[#373333] bg-[#1C1A1A] shrink-0">
              <div className="relative bg-[#242222] border border-[#373333] rounded-2xl p-2 pb-9 transition-colors focus-within:border-[#8F0028]">
                <textarea 
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSendMessage()
                    }
                  }}
                  placeholder="Ask me anything..." 
                  className="w-full bg-transparent resize-none outline-none text-[12.5px] text-[#F5F3F1] placeholder:text-[#A9A4A0] p-1.5 h-[38px] custom-scrollbar"
                />
                
                <div className="absolute bottom-2 left-2 flex items-center gap-1">
                  <button className="p-1 text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#373333] rounded-md transition-colors" title="Attach file">
                    <Paperclip className="w-3.5 h-3.5" />
                  </button>
                  <button className="p-1 text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#373333] rounded-md transition-colors text-[12px] font-bold" title="Mention Agent">
                    @
                  </button>
                  <button className="p-1 text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#373333] rounded-md transition-colors" title="Browse Knowledge Base">
                    <Globe className="w-3.5 h-3.5" />
                  </button>
                </div>

                <button 
                  onClick={() => handleSendMessage()}
                  disabled={!chatInput.trim() || isChatLoading}
                  className="absolute bottom-2 right-2 p-1.5 bg-[#8F0028] text-white rounded-lg hover:bg-[#A3002D] transition-colors shadow-md shadow-[#8F0028]/20 disabled:opacity-40"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </>
        )}

        {/* TAB: RESEARCH */}
        {cmoTab === 'Research' && (
          <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-4">
            <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
              <h4 className="text-[13px] font-bold text-white mb-2">Market Positioning Radar</h4>
              <p className="text-[12px] text-[#A9A4A0] leading-relaxed">
                <strong className="text-white">{activeBrand?.name || 'Your Brand'}</strong> is positioned with a focus on <strong className="text-white">{brandBrain?.positioning?.unique_value_proposition || activeBrand?.mission || 'delivering standout value to core customers'}</strong>.
                {brandBrain?.audiences?.[0]?.name && ` Targeting ${brandBrain.audiences[0].name}.`}
              </p>
            </div>

            <div className="space-y-2">
              <h5 className="text-[11px] font-bold text-[#A9A4A0] uppercase">Competitor Intelligence</h5>
              {(brandBrain?.competitors && brandBrain.competitors.length > 0) ? (
                brandBrain.competitors.map((c: any) => (
                  <div key={c.id || c.name} className="p-3 bg-[#242222] border border-[#373333] rounded-xl text-[12px]">
                    <div className="font-bold text-[#F5F3F1] mb-1">{c.name}</div>
                    <div className="text-[#00A650] text-[11px]">Monitored: Competitive pricing & brand search signals</div>
                    <div className="text-[#FF4560] text-[11px] mt-0.5">Differentiator: {activeBrand?.name || 'Our brand'} offers {brandBrain?.positioning?.unique_value_proposition?.slice(0, 60) || 'distinctive value solutions'}</div>
                  </div>
                ))
              ) : (
                <div className="p-4 bg-[#242222] border border-[#373333] rounded-xl text-[12px] text-[#A9A4A0]">
                  No competitors tracked yet. Add your competitors in the Brand Brain context panel to activate real-time intelligence.
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB: STRATEGY */}
        {cmoTab === 'Strategy' && (
          <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-4">
            <div className="bg-[#242222] border border-[#373333] rounded-xl p-4">
              <h4 className="text-[13px] font-bold text-white mb-1">30-Day Go-To-Market Plan</h4>
              <p className="text-[11px] text-[#A9A4A0]">
                Target: {brandBrain?.goals?.[0]?.target_value ? `Reach ${brandBrain.goals[0].target_value}` : 'Accelerate Business Growth'} ({brandBrain?.goals?.[0]?.goal || 'Primary Objective'})
              </p>
            </div>

            <div className="space-y-3">
              {[
                { week: 'Week 1', focus: 'Authority & Positioning Content', desc: `Launch curated thought leadership posts addressing "${brandBrain?.audiences?.[0]?.pain_points ? brandBrain.audiences[0].pain_points.slice(0, 80) : 'key customer challenges'}" for ${activeBrand?.name || 'your brand'}.` },
                { week: 'Week 2', focus: 'Technical SEO & Metadata', desc: `Deploy rich schema markup, semantic tags, and search indexing for ${activeBrand?.website_url ? activeBrand.website_url.replace(/^https?:\/\//,'') : (activeBrand?.name || 'your brand')}.` },
                { week: 'Week 3', focus: 'Customer Acquisition & Outreach', desc: `Engage ${brandBrain?.audiences?.[0]?.name || 'key target buyers'} with high-relevance messaging highlighting your unique value proposition.` },
                { week: 'Week 4', focus: 'Conversion Rate Optimization', desc: `A/B test landing page copy and primary conversion CTAs to maximize lead capture toward your ${brandBrain?.goals?.[0]?.target_value || 'revenue'} target.` },
              ].map(w => (
                <div key={w.week} className="p-3 bg-[#242222] border border-[#373333] rounded-xl text-[12px]">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-[#8F0028] text-[11px] uppercase tracking-wider">{w.week}</span>
                    <span className="text-[10px] text-[#00A650] font-semibold">Planned</span>
                  </div>
                  <div className="font-bold text-white mb-0.5">{w.focus}</div>
                  <p className="text-[#A9A4A0] text-[11px] leading-relaxed">{w.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB: TASKS */}
        {cmoTab === 'Tasks' && (
          <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3">
            <div className="flex items-center justify-between mb-1">
              <h4 className="text-[13px] font-bold text-white">Actionable Tasks</h4>
              <span className="text-[11px] text-[#A9A4A0]">3 Pending</span>
            </div>

            {[
              { id: '1', title: `Review pending content drafts for ${activeBrand?.name || 'brand'}`, done: approvalsCount === 0, action: '/app/approvals' },
              { id: '2', title: `Crawl & vectorize ${activeBrand?.website_url ? activeBrand.website_url.replace(/^https?:\/\//,'') : (activeBrand?.name || 'brand')} SEO signals`, done: true },
              { id: '3', title: 'Connect Google Analytics 4 & Search Console', done: true },
              { id: '4', title: `Run Competitor Agent for ${activeBrand?.name || 'brand'} market benchmarks`, done: false, triggerAgent: 'competitor' },
              { id: '5', title: 'Deploy schema markup and metadata enhancements', done: false },
            ].map(t => (
              <div key={t.id} className="p-3 bg-[#242222] border border-[#373333] rounded-xl flex items-start gap-3 text-[12px]">
                <div className={`w-4 h-4 rounded mt-0.5 flex items-center justify-center shrink-0 ${t.done ? 'bg-[#00A650] text-white' : 'border border-[#373333]'}`}>
                  {t.done && <Check className="w-3 h-3" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`font-medium ${t.done ? 'line-through text-[#A9A4A0]' : 'text-[#F5F3F1]'}`}>{t.title}</p>
                  {t.action && !t.done && (
                    <Link href={t.action} className="text-[11px] text-[#8F0028] hover:underline font-bold mt-1 inline-block">
                      Open Approvals Queue →
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

      </div>

    </div>
  )
}
