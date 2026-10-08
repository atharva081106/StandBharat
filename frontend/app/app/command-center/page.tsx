"use client"
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useState, useEffect } from 'react'
import { useDashboard, useOpportunity, useOrchestrator } from '@/lib/providers/MockProvider'
import { Switch } from '@/components/ui/switch'

const data = [
  { name: 'Mon', revenue: 4000, leads: 240 },
  { name: 'Tue', revenue: 3000, leads: 139 },
  { name: 'Wed', revenue: 2000, leads: 980 },
  { name: 'Thu', revenue: 2780, leads: 390 },
  { name: 'Fri', revenue: 1890, leads: 480 },
  { name: 'Sat', revenue: 2390, leads: 380 },
  { name: 'Sun', revenue: 3490, leads: 430 },
]

export default function CommandCenter() {
  const dashboardProvider = useDashboard()
  const oppProvider = useOpportunity()
  const orchestratorProvider = useOrchestrator()
  const [dataModel, setDataModel] = useState<any>(null)
  const [orchestratorConfig, setOrchestratorConfig] = useState<any>(null)
  const [orchestratorRuns, setOrchestratorRuns] = useState<any[]>([])
  
  const loadDashboard = async () => {
    const data = await dashboardProvider.getDashboard()
    setDataModel(data)
  }

  const loadOrchestrator = async () => {
    try {
      const config = await orchestratorProvider.getStatus()
      const runs = await orchestratorProvider.getRuns()
      setOrchestratorConfig(config)
      setOrchestratorRuns(runs || [])
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    loadDashboard()
    loadOrchestrator()
  }, [])

  const [approvedItems, setApprovedItems] = useState<string[]>([])

  const handleExecute = async (id: string) => {
    await oppProvider.executeOpportunity(id)
    await loadDashboard()
  }

  const handleApprove = (id: string) => {
    setApprovedItems(prev => [...prev, id])
  }

  if (!dataModel) {
    return (
      <div className="h-full flex items-center justify-center text-[#858585]">
        <div className="flex flex-col items-center gap-3">
          <div className="h-10 w-10 rounded-full border-4 border-[#E8E4DC] border-t-[#800020] animate-spin"></div>
          <p className="text-sm font-bold tracking-wider uppercase">Loading intelligence...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-10 max-w-7xl mx-auto pb-12">
      {/* Context & Welcome */}
      <div className="flex flex-col gap-2 border-b border-[#E8E4DC] pb-8 pt-4">
        <div className="flex items-center justify-between">
          <h1 className="text-4xl font-bold tracking-tight text-[#111111]">Good morning.</h1>
          {process.env.NEXT_PUBLIC_DATA_MODE === 'mock' && (
            <Badge className="bg-[#FAF8F3] text-[#800020] border border-[#800020]/20 font-bold hover:bg-[#FAF8F3]">MOCK DATA</Badge>
          )}
        </div>
        <p className="text-[#5A5A5A] font-medium text-lg">Your marketing operation is running smoothly. AI CMO has identified 1 high-priority action.</p>
      </div>
      
      {/* AI Recommendation */}
      <div className="bg-[#FDF8F6] border border-[#800020]/20 rounded-[24px] p-6 sm:p-8 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#800020]/5 rounded-full blur-3xl pointer-events-none translate-x-1/3 -translate-y-1/3"></div>
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-[#800020]">
              <svg className="w-4 h-4 animate-pulse" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
              AI CMO Recommendation
            </div>
            <h2 className="text-2xl font-bold text-[#111111] tracking-tight">Optimize Q4 Lead Generation Campaign</h2>
            <p className="text-[#5A5A5A] text-[15px] font-medium max-w-2xl">Recent analytics indicate a drop in CTR. Running the Growth Agent is highly recommended to A/B test new creative angles.</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 shrink-0">
            <Button className="h-12 px-6 bg-[#800020] hover:bg-[#5C0017] text-white font-bold text-sm rounded-xl transition-all shadow-xl shadow-[#800020]/20 hover:-translate-y-0.5">
              Execute Recommendation
            </Button>
            <Button variant="outline" className="h-12 px-6 bg-white border-[#E8E4DC] text-[#111111] font-bold text-sm rounded-xl hover:bg-[#FAF8F3]">
              Dismiss
            </Button>
          </div>
        </div>
      </div>

      {/* Business Signals */}
      <div className="space-y-5">
        <h2 className="text-[22px] font-bold tracking-tight text-[#111111]">Business Signals</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {dataModel.kpis && dataModel.kpis.length > 0 ? (
            dataModel.kpis.map((kpi: any) => (
              <div key={kpi.label} className="bg-white border border-[#E8E4DC] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-[11px] font-bold text-[#858585] uppercase tracking-wider mb-2">{kpi.label}</div>
                <div className="text-3xl font-bold text-[#111111] tracking-tight mb-2">{kpi.value}</div>
                <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#008A2E]/10 text-[#008A2E] text-[11px] font-bold">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg>
                  {kpi.change} from last period
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-4 bg-[#FAF8F3] border border-dashed border-[#E8E4DC] rounded-2xl flex flex-col items-center justify-center py-10 text-center">
              <p className="text-[#111111] font-bold">No signals available yet</p>
              <p className="text-sm text-[#5A5A5A] mt-1 font-medium">Connect a data source to unlock marketing insights.</p>
              <Button variant="outline" className="mt-5 border-[#E8E4DC] font-bold rounded-xl">Connect Data Source</Button>
            </div>
          )}
        </div>
      </div>

      {/* Performance Intelligence */}
      <div className="space-y-5">
        <h2 className="text-[22px] font-bold tracking-tight text-[#111111]">Performance Intelligence</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1 bg-white border border-[#E8E4DC] rounded-2xl p-6 shadow-sm">
             <div className="text-[11px] font-bold text-[#858585] uppercase tracking-wider mb-6">Status</div>
             <div className="space-y-6">
                <div>
                   <div className="flex items-center gap-2 mb-1.5">
                     <span className="relative flex h-2.5 w-2.5">
                       <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#008A2E] opacity-75"></span>
                       <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#008A2E]"></span>
                     </span>
                     <span className="text-sm font-bold text-[#111111]">Tracking Active</span>
                   </div>
                   <p className="text-[13px] text-[#5A5A5A] font-medium ml-4.5">Monitoring LinkedIn for brand mentions.</p>
                </div>
                <div className="pt-4 border-t border-[#E8E4DC]">
                  <p className="text-[11px] font-bold text-[#800020] uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                    Top Trend
                  </p>
                  <p className="text-sm text-[#111111] font-medium leading-relaxed">Educational posts are seeing 15% higher engagement than promotional.</p>
                </div>
             </div>
          </div>
          
          <div className="md:col-span-2 bg-white border border-[#E8E4DC] rounded-2xl overflow-hidden shadow-sm flex flex-col">
             <div className="px-6 py-5 border-b border-[#E8E4DC] bg-[#FAF8F3]/50">
                <div className="text-[11px] font-bold text-[#858585] uppercase tracking-wider">Top Performing Content</div>
             </div>
             <div className="divide-y divide-[#E8E4DC] flex-1 flex flex-col">
                {[1, 2].map(i => (
                  <div key={i} className="p-6 flex flex-col sm:flex-row gap-5 items-start sm:items-center justify-between hover:bg-[#FAF8F3] transition-colors">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 border border-[#E8E4DC] rounded text-[9px] font-bold uppercase text-[#5A5A5A]">LinkedIn</span>
                        <p className="text-[15px] font-bold text-[#111111]">"How AI changes marketing workflows..."</p>
                      </div>
                      <p className="text-[12px] font-medium text-[#858585]">Published 2 days ago</p>
                    </div>
                    <div className="flex gap-6 shrink-0">
                      <div className="text-center">
                        <p className="text-lg font-bold text-[#111111]">4.2k</p>
                        <p className="text-[9px] font-bold text-[#858585] uppercase tracking-wider mt-0.5">Impressions</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold text-[#111111]">342</p>
                        <p className="text-[9px] font-bold text-[#858585] uppercase tracking-wider mt-0.5">Engagements</p>
                      </div>
                    </div>
                  </div>
                ))}
             </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Opportunities */}
        <div className="lg:col-span-2 space-y-5">
          <h2 className="text-[22px] font-bold tracking-tight text-[#111111]">AI Opportunities</h2>
          <div className="bg-white border border-[#E8E4DC] rounded-2xl overflow-hidden shadow-sm">
             {dataModel.opportunities && dataModel.opportunities.length > 0 ? (
               <div className="divide-y divide-[#E8E4DC]">
                 {dataModel.opportunities.slice(0, 3).map((opp: any) => (
                   <div key={opp.id} className="p-6 flex flex-col sm:flex-row gap-5 items-start sm:items-center justify-between hover:bg-[#FAF8F3] transition-colors">
                     <div className="space-y-3 flex-1">
                       <div className="flex items-center gap-3">
                         <p className="font-bold text-[#111111] text-[15px]">{opp.title}</p>
                         <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
                           opp.impact === 'High' ? 'bg-[#800020]/10 text-[#800020]' : 'bg-[#E8E4DC]/50 text-[#5A5A5A]'
                         }`}>
                           {opp.impact} Impact
                         </span>
                       </div>
                       <p className="text-sm text-[#5A5A5A] font-medium leading-relaxed">{opp.description || "Identified an opportunity to improve marketing outcomes based on recent competitive analysis."}</p>
                       <div className="flex items-center gap-5 text-[11px] text-[#858585] font-bold uppercase tracking-wider">
                         <span>Confidence <span className="text-[#111111]">{opp.confidence || '80%'}</span></span>
                         <span>Effort <span className="text-[#111111]">Medium</span></span>
                       </div>
                     </div>
                     <div className="flex gap-3 w-full sm:w-auto mt-2 sm:mt-0">
                       <Button size="sm" variant="outline" className="flex-1 border-[#E8E4DC] font-bold rounded-lg h-9">Review</Button>
                       <Button size="sm" className="flex-1 bg-[#111111] hover:bg-[#333333] text-white font-bold rounded-lg h-9" onClick={() => handleExecute(opp.id)}>Execute</Button>
                     </div>
                   </div>
                 ))}
               </div>
             ) : (
               <div className="flex flex-col items-center justify-center py-14 text-center px-6">
                 <p className="text-[#111111] font-bold">No opportunities identified</p>
                 <p className="text-sm text-[#5A5A5A] mt-1 font-medium">Run an intelligence agent to discover new growth opportunities.</p>
                 <Button variant="outline" className="mt-5 border-[#E8E4DC] font-bold rounded-xl">Run Growth Agent</Button>
               </div>
             )}
          </div>
        </div>

        {/* Needs Attention */}
        <div className="space-y-5">
          <h2 className="text-[22px] font-bold tracking-tight text-[#111111]">Needs Attention</h2>
          <div className="bg-white border border-[#E8E4DC] rounded-2xl overflow-hidden shadow-sm divide-y divide-[#E8E4DC]">
            {/* Simulated Approvals */}
            <div className="p-6 flex items-start gap-4">
              <div className="h-10 w-10 rounded-xl bg-orange-50 border border-orange-100 text-orange-600 flex items-center justify-center shrink-0 shadow-sm">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
              </div>
              <div>
                <p className="text-sm font-bold text-[#111111]">Content Approval Required</p>
                <p className="text-[13px] text-[#5A5A5A] font-medium mt-1">AI CMO drafted "Q4 Launch Post"</p>
                <div className="flex gap-2 mt-4">
                  <Button size="sm" className="bg-[#111111] hover:bg-[#333333] text-white font-bold rounded-lg h-8 px-4 text-xs">Review Draft</Button>
                </div>
              </div>
            </div>
            
            {/* System Alerts */}
            <div className="p-6 flex items-start gap-4 bg-[#FDF8F6]">
              <div className="h-10 w-10 rounded-xl bg-[#800020]/10 border border-[#800020]/20 text-[#800020] flex items-center justify-center shrink-0 shadow-sm">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              </div>
              <div>
                <p className="text-sm font-bold text-[#800020]">LinkedIn Disconnected</p>
                <p className="text-[13px] text-[#800020]/70 font-medium mt-1">Authentication token expired.</p>
                <a href="#" className="text-xs font-bold uppercase tracking-wider text-[#800020] underline mt-3 inline-block hover:text-[#5C0017]">Reconnect</a>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Activity & Orchestrator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Recent Activity */}
        <div className="space-y-5">
          <h2 className="text-[22px] font-bold tracking-tight text-[#111111]">Recent Activity</h2>
          <div className="bg-white border border-[#E8E4DC] rounded-2xl overflow-hidden shadow-sm h-full">
            {dataModel.recent_activity && dataModel.recent_activity.length > 0 ? (
              <div className="p-8 space-y-8">
                {dataModel.recent_activity.slice(0, 4).map((activity: any, index: number) => (
                  <div key={activity.id} className="relative pl-8">
                    {index !== dataModel.recent_activity.slice(0, 4).length - 1 && (
                      <div className="absolute left-[15px] top-6 bottom-[-32px] w-[2px] bg-[#E8E4DC]"></div>
                    )}
                    <div className="absolute left-0 top-1 h-8 w-8 rounded-full bg-white border-2 border-[#E8E4DC] flex items-center justify-center">
                      <div className="h-2.5 w-2.5 rounded-full bg-[#800020]"></div>
                    </div>
                    <div>
                      <p className="text-[15px] text-[#111111] font-medium leading-snug"><span className="font-bold">{activity.type}</span> {activity.description}</p>
                      <p className="text-[11px] font-bold text-[#858585] uppercase tracking-wider mt-1.5">2 hours ago</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-center h-full">
                <p className="text-sm font-medium text-[#5A5A5A]">No recent activity.</p>
              </div>
            )}
          </div>
        </div>

        {/* Orchestrator Status */}
        <div className="space-y-5">
          <h2 className="text-[22px] font-bold tracking-tight text-[#111111]">Orchestrator</h2>
          <div className="bg-white border border-[#E8E4DC] rounded-2xl overflow-hidden shadow-sm h-full flex flex-col">
            <div className="px-6 py-5 border-b border-[#E8E4DC] flex flex-row items-center justify-between bg-[#FAF8F3]/50">
              <div>
                <h3 className="text-sm font-bold text-[#111111] uppercase tracking-wider">Autonomous Mode</h3>
                <p className="text-[12px] font-medium text-[#5A5A5A] mt-0.5">Control AI operation.</p>
              </div>
              <div className="flex items-center gap-4">
                <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                  orchestratorConfig?.mode === 'AUTONOMOUS' ? 'bg-[#008A2E]/10 text-[#008A2E]' : 
                  orchestratorConfig?.mode === 'ASSISTED' ? 'bg-orange-100 text-orange-700' : 'bg-[#E8E4DC] text-[#5A5A5A]'
                }`}>
                  {orchestratorConfig?.mode || 'OFF'}
                </span>
                <Switch 
                  checked={orchestratorConfig?.mode === 'AUTONOMOUS'} 
                  onCheckedChange={async (checked) => {
                    await orchestratorProvider.updateStatus(checked ? 'AUTONOMOUS' : 'OFF')
                    loadOrchestrator()
                  }}
                  className="data-[state=checked]:bg-[#800020]"
                />
              </div>
            </div>
            <div className="flex-1 flex flex-col">
               <div className="divide-y divide-[#E8E4DC] flex-1">
                 {orchestratorRuns.length > 0 ? orchestratorRuns.slice(0, 3).map((run: any) => (
                   <div key={run.id} className="p-6 flex flex-col gap-3 hover:bg-[#FAF8F3] transition-colors">
                     <div className="flex items-center justify-between">
                       <span className="text-sm font-bold text-[#111111]">Agent: {run.agent_id || 'System'}</span>
                       <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
                         run.decision === 'RUN' ? 'bg-[#111111] text-white' : 'bg-[#E8E4DC] text-[#5A5A5A]'
                       }`}>
                         {run.decision}
                       </span>
                     </div>
                     <p className="text-[13px] font-medium text-[#5A5A5A] leading-relaxed">{run.reason}</p>
                     <p className="text-[11px] font-bold text-[#858585] uppercase tracking-wider">{new Date(run.started_at).toLocaleString()}</p>
                   </div>
                 )) : (
                   <div className="p-8 flex flex-col items-center justify-center h-full text-center">
                     <p className="text-sm font-medium text-[#5A5A5A]">No orchestrator history yet.</p>
                   </div>
                 )}
               </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
