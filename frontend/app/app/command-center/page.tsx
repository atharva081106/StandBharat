"use client"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
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
      <div className="h-full flex items-center justify-center text-[var(--color-text-muted)]">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 rounded-full border-4 border-[var(--color-bg-subtle)] border-t-[var(--color-brand-accent)] animate-spin"></div>
          <p className="text-sm">Loading intelligence...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Context & Welcome */}
      <div className="flex flex-col gap-2 border-b border-[var(--color-border-primary)] pb-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-text-primary)]">Good morning.</h1>
          {process.env.NEXT_PUBLIC_DATA_MODE === 'mock' && (
            <Badge variant="warning">MOCK DATA</Badge>
          )}
        </div>
        <p className="text-[var(--color-text-tertiary)] text-lg">Your marketing operation is running smoothly. AI CMO has identified 1 high-priority action.</p>
      </div>
      
      {/* AI Recommendation */}
      <Card className="border-[var(--color-brand-accent)] border-l-4">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold uppercase tracking-wider text-[var(--color-brand-accent)] flex items-center gap-2">
            AI CMO Recommendation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <p className="text-lg font-medium text-[var(--color-text-primary)]">Optimize Q4 Lead Generation Campaign</p>
              <p className="text-[var(--color-text-tertiary)] text-sm">Recent analytics indicate a drop in CTR. Running the Growth Agent is highly recommended.</p>
            </div>
            <div className="flex gap-2 shrink-0">
              <Button>Execute Recommendation</Button>
              <Button variant="outline">Dismiss</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Business Signals */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Business Signals</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {dataModel.kpis && dataModel.kpis.length > 0 ? (
            dataModel.kpis.map((kpi: any) => (
              <Card key={kpi.label}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">{kpi.label}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-[var(--color-text-primary)]">{kpi.value}</div>
                  <p className="text-xs font-medium mt-1 text-green-600 flex items-center gap-1">
                    ↑ {kpi.change} from last period
                  </p>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card className="col-span-4 bg-[var(--color-bg-subtle)] border-dashed">
              <CardContent className="flex flex-col items-center justify-center py-8 text-center">
                <p className="text-[var(--color-text-primary)] font-medium">No signals available yet</p>
                <p className="text-sm text-[var(--color-text-tertiary)] mt-1">Connect a data source to unlock marketing insights.</p>
                <Button variant="outline" className="mt-4">Connect Data Source</Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Performance Intelligence */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Performance Intelligence</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="md:col-span-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">
                Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500"></div>
                  <span className="text-sm font-medium">Tracking Active</span>
                </div>
                <p className="text-xs text-[var(--color-text-tertiary)]">Monitoring LinkedIn.</p>
                <div className="pt-2 border-t border-[var(--color-border-primary)]">
                  <p className="text-xs font-semibold text-[var(--color-text-primary)]">Top Trend</p>
                  <p className="text-sm text-[var(--color-text-tertiary)] mt-1 line-clamp-2">Educational posts are seeing 15% higher engagement than promotional.</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="md:col-span-2">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">
                Top Performing Content
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-[var(--color-border-primary)]">
                {[1, 2].map(i => (
                  <div key={i} className="p-4 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between hover:bg-[var(--color-bg-subtle)] transition-colors">
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-[10px]">LinkedIn</Badge>
                        <p className="text-sm font-medium text-[var(--color-text-primary)]">"How AI changes marketing workflows..."</p>
                      </div>
                      <p className="text-xs text-[var(--color-text-tertiary)]">Published 2 days ago</p>
                    </div>
                    <div className="flex gap-4 text-sm">
                      <div className="text-center">
                        <p className="font-bold">4.2k</p>
                        <p className="text-[10px] text-[var(--color-text-muted)] uppercase">Impressions</p>
                      </div>
                      <div className="text-center">
                        <p className="font-bold">342</p>
                        <p className="text-[10px] text-[var(--color-text-muted)] uppercase">Engagements</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Opportunities */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold tracking-tight">AI Opportunities</h2>
          <Card>
            <CardContent className="p-0">
              {dataModel.opportunities && dataModel.opportunities.length > 0 ? (
                <div className="divide-y divide-[var(--color-border-primary)]">
                  {dataModel.opportunities.slice(0, 3).map((opp: any) => (
                    <div key={opp.id} className="p-6 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between hover:bg-[var(--color-bg-subtle)] transition-colors">
                      <div className="space-y-2 flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-semibold text-[var(--color-text-primary)]">{opp.title}</p>
                          <Badge variant="default" className="text-[10px] uppercase">
                            {opp.impact} Impact
                          </Badge>
                        </div>
                        <p className="text-sm text-[var(--color-text-tertiary)] line-clamp-2">{opp.description || "Identified an opportunity to improve marketing outcomes based on recent competitive analysis and growth data."}</p>
                        <div className="flex items-center gap-4 text-xs text-[var(--color-text-muted)] font-medium">
                          <span>Confidence: <span className="text-[var(--color-text-primary)]">{opp.confidence || '80%'}</span></span>
                          <span>Effort: <span className="text-[var(--color-text-primary)]">Medium</span></span>
                        </div>
                      </div>
                      <div className="flex gap-2 shrink-0 w-full md:w-auto mt-2 md:mt-0">
                        <Button size="sm" variant="outline" className="flex-1">Review</Button>
                        <Button size="sm" className="flex-1" onClick={() => handleExecute(opp.id)}>Execute</Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center px-4">
                  <p className="text-[var(--color-text-primary)] font-medium">No opportunities identified</p>
                  <p className="text-sm text-[var(--color-text-tertiary)] mt-1">Run an intelligence agent to discover new growth opportunities.</p>
                  <Button variant="outline" className="mt-4">Run Growth Agent</Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Needs Attention / Approvals */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold tracking-tight">Needs Attention</h2>
          <Card>
            <CardContent className="p-0">
              <div className="divide-y divide-[var(--color-border-primary)]">
                {/* Simulated Approvals */}
                <div className="p-5 flex items-start gap-3">
                  <div className="h-8 w-8 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center shrink-0">
                    <span className="text-xs font-bold">C</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--color-text-primary)]">Content Approval Required</p>
                    <p className="text-xs text-[var(--color-text-tertiary)] mt-1">AI CMO drafted "Q4 Launch Post"</p>
                    <div className="flex gap-2 mt-3">
                      <Button size="sm">Review Draft</Button>
                    </div>
                  </div>
                </div>
                
                {/* System Alerts */}
                <div className="p-5 flex items-start gap-3 bg-amber-50">
                  <div className="h-8 w-8 rounded-full bg-amber-200 text-amber-800 flex items-center justify-center shrink-0">
                    <span className="text-xs font-bold">!</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-amber-900">LinkedIn Disconnected</p>
                    <p className="text-xs text-amber-800 mt-1">Authentication token expired.</p>
                    <a href="#" className="text-xs font-medium underline mt-2 inline-block text-amber-900">Reconnect</a>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      
      {/* Activity & Orchestrator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Recent Activity */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold tracking-tight">Recent Activity</h2>
          <Card>
            <CardContent className="p-0">
              {dataModel.recent_activity && dataModel.recent_activity.length > 0 ? (
                <div className="p-6 space-y-6">
                  {dataModel.recent_activity.slice(0, 4).map((activity: any, index: number) => (
                    <div key={activity.id} className="relative pl-6">
                      {index !== dataModel.recent_activity.slice(0, 4).length - 1 && (
                        <div className="absolute left-[11px] top-6 bottom-[-24px] w-px bg-[var(--color-border-primary)]"></div>
                      )}
                      <div className="absolute left-0 top-1.5 h-6 w-6 rounded-full bg-[var(--color-bg-primary)] border border-[var(--color-border-primary)] flex items-center justify-center">
                        <div className="h-2 w-2 rounded-full bg-[var(--color-text-tertiary)]"></div>
                      </div>
                      <div>
                        <p className="text-sm text-[var(--color-text-primary)]"><span className="font-medium">{activity.type}</span> {activity.description}</p>
                        <p className="text-xs text-[var(--color-text-muted)] mt-1">2 hours ago</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-12 text-center">
                  <p className="text-sm text-[var(--color-text-tertiary)]">No recent activity.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Orchestrator Status */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold tracking-tight">Orchestrator</h2>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-[var(--color-border-primary)]">
              <div>
                <CardTitle className="text-base font-semibold">Autonomous Mode</CardTitle>
                <p className="text-xs text-[var(--color-text-tertiary)] mt-1">Control AI operation.</p>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={orchestratorConfig?.mode === 'AUTONOMOUS' ? 'success' : orchestratorConfig?.mode === 'ASSISTED' ? 'warning' : 'secondary'}>
                  {orchestratorConfig?.mode || 'OFF'}
                </Badge>
                <Switch 
                  checked={orchestratorConfig?.mode === 'AUTONOMOUS'} 
                  onCheckedChange={async (checked) => {
                    await orchestratorProvider.updateStatus(checked ? 'AUTONOMOUS' : 'OFF')
                    loadOrchestrator()
                  }}
                />
              </div>
            </CardHeader>
            <CardContent className="pt-4 p-0">
               <div className="divide-y divide-[var(--color-border-primary)]">
                 {orchestratorRuns.length > 0 ? orchestratorRuns.slice(0, 3).map((run: any) => (
                   <div key={run.id} className="p-4 flex flex-col gap-2 hover:bg-[var(--color-bg-subtle)] transition-colors">
                     <div className="flex items-center justify-between">
                       <span className="text-sm font-medium text-[var(--color-text-primary)]">Agent: {run.agent_id || 'System'}</span>
                       <Badge variant={run.decision === 'RUN' ? 'default' : 'secondary'} className="text-[10px]">
                         {run.decision}
                       </Badge>
                     </div>
                     <p className="text-sm text-[var(--color-text-tertiary)] leading-snug">{run.reason}</p>
                     <p className="text-xs font-medium text-[var(--color-text-muted)]">{new Date(run.started_at).toLocaleString()}</p>
                   </div>
                 )) : (
                   <div className="p-8 text-center">
                     <p className="text-sm text-[var(--color-text-tertiary)]">No orchestrator history yet.</p>
                   </div>
                 )}
               </div>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  )
}
