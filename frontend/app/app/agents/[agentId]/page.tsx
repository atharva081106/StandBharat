"use client"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useAppProvider } from '@/lib/providers'
import { useEffect, useState, useMemo } from 'react'

export default function AgentDetail({ params }: { params: { agentId: string } }) {
  const { agents } = useAppProvider()
  const [agent, setAgent] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)

  const fetchRuns = async () => {
    try {
      const data = await agents.getAgentRuns(params.agentId)
      setRuns(data)
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    const fetchAgent = async () => {
      try {
        const data = await agents.getAgent(params.agentId)
        setAgent(data)
        await fetchRuns()
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchAgent()
  }, [params.agentId, agents])

  const handleRun = async () => {
    setRunning(true)
    try {
      await agents.runAgent(params.agentId, { input_data: {} })
      // Poll a few times to get the updated status
      setTimeout(fetchRuns, 2000)
      setTimeout(fetchRuns, 5000)
      setTimeout(fetchRuns, 10000)
    } catch(e) {
      console.error(e)
    } finally {
      setRunning(false)
      await fetchRuns()
    }
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center text-[var(--color-text-muted)]">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 rounded-full border-4 border-[var(--color-bg-subtle)] border-t-[var(--color-brand-accent)] animate-spin"></div>
          <p className="text-sm font-medium">Loading Agent Details...</p>
        </div>
      </div>
    )
  }

  if (!agent) {
    return (
      <div className="h-full flex items-center justify-center text-red-500">
        <div className="flex flex-col items-center gap-2">
          <p className="text-lg font-medium">Agent not found</p>
          <Button variant="outline" onClick={() => window.history.back()}>Go Back</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--color-border-primary)] pb-6">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-text-primary)] capitalize">{agent.name}</h1>
            <Badge variant={agent.status === 'ACTIVE' ? 'success' : agent.status === 'WAITING' ? 'warning' : 'secondary'} className="text-[10px] uppercase tracking-wider">
              {agent.status || "IDLE"}
            </Badge>
          </div>
          <p className="text-[var(--color-text-tertiary)] text-lg">{agent.description}</p>
        </div>
        <div className="flex gap-3 shrink-0">
          <Button variant="outline">Pause Agent</Button>
          <Button onClick={handleRun} disabled={running} className="min-w-[120px]">
            {running ? (
              <span className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
                Starting...
              </span>
            ) : "Run Now"}
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card className="flex flex-col h-full border-[var(--color-border-primary)]">
             <CardHeader className="border-b border-[var(--color-border-primary)] bg-[var(--color-bg-subtle)] pb-4">
               <CardTitle className="flex justify-between items-center text-base">
                 <span>Execution History</span>
                 <Button variant="outline" size="sm" onClick={fetchRuns} className="h-8">Refresh</Button>
               </CardTitle>
             </CardHeader>
             <CardContent className="p-0 flex-1">
               {runs.length > 0 ? (
                 <div className="divide-y divide-[var(--color-border-primary)]">
                   {runs.map(run => (
                     <div key={run.id} className="p-5 hover:bg-[var(--color-bg-subtle)] transition-colors">
                       <div className="flex justify-between items-start mb-3">
                         <div className="flex items-center gap-3">
                           <span className="font-semibold text-[var(--color-text-primary)] text-sm">{new Date(run.created_at).toLocaleString()}</span>
                           <span className="text-xs text-[var(--color-text-muted)] font-mono">{run.id.substring(0,8)}</span>
                         </div>
                         <Badge variant={run.status === 'SUCCESS' ? 'success' : run.status === 'FAILED' ? 'danger' : run.status === 'RUNNING' ? 'warning' : 'secondary'} className="text-[10px] uppercase tracking-wider">
                           {run.status}
                         </Badge>
                       </div>
                       
                       {run.error_message && (
                         <div className="mt-3 p-3 bg-red-50 text-red-700 text-sm rounded-md border border-red-100 flex items-start gap-2">
                           <span className="font-bold shrink-0">!</span>
                           <span className="break-all">{run.error_message}</span>
                         </div>
                       )}
                       
                       {run.result_data && (
                         <div className="mt-3">
                           <div className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Output</div>
                           <pre className="text-xs text-[var(--color-text-secondary)] bg-[var(--color-bg-primary)] p-3 rounded-md border border-[var(--color-border-primary)] max-h-60 overflow-auto whitespace-pre-wrap font-mono">
                             {JSON.stringify(run.result_data, null, 2)}
                           </pre>
                         </div>
                       )}
                     </div>
                   ))}
                 </div>
               ) : (
                 <div className="flex flex-col items-center justify-center py-16 text-center px-4">
                   <p className="text-[var(--color-text-primary)] font-medium">No execution history</p>
                   <p className="text-sm text-[var(--color-text-tertiary)] mt-1">This agent hasn't been run yet.</p>
                   <Button variant="outline" className="mt-4" onClick={handleRun}>Run First Task</Button>
                 </div>
               )}
             </CardContent>
          </Card>
        </div>
        
        <div className="space-y-6">
          <Card className="border-[var(--color-border-primary)]">
             <CardHeader className="border-b border-[var(--color-border-primary)] bg-[var(--color-bg-subtle)] pb-4">
               <CardTitle className="text-base">Capabilities</CardTitle>
             </CardHeader>
             <CardContent className="pt-4">
               <ul className="space-y-3">
                 {agent.capabilities?.map((cap: string, i: number) => (
                   <li key={i} className="flex items-start gap-2 text-sm text-[var(--color-text-secondary)]">
                     <span className="text-[var(--color-brand-accent)] mt-0.5">•</span>
                     <span className="leading-snug">{cap}</span>
                   </li>
                 )) || (
                   <li className="text-sm text-[var(--color-text-muted)] italic">No specific capabilities listed</li>
                 )}
               </ul>
             </CardContent>
          </Card>
          
          <Card className="border-[var(--color-border-primary)]">
             <CardHeader className="border-b border-[var(--color-border-primary)] bg-[var(--color-bg-subtle)] pb-4">
               <CardTitle className="text-base">Configuration</CardTitle>
             </CardHeader>
             <CardContent className="pt-4">
               <div className="space-y-4">
                 <div>
                   <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider block mb-1">Model Provider</span>
                   <span className="text-sm font-medium text-[var(--color-text-primary)]">OpenAI GPT-4o</span>
                 </div>
                 <div>
                   <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider block mb-1">Schedule</span>
                   <span className="text-sm font-medium text-[var(--color-text-primary)]">Orchestrator Managed</span>
                 </div>
                 <Button variant="outline" className="w-full mt-2">Edit Configuration</Button>
               </div>
             </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
