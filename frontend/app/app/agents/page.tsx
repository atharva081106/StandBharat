"use client"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Bot } from 'lucide-react'
import { useAppProvider } from '@/lib/providers'
import { useEffect, useState } from 'react'
import Link from 'next/link'

export default function Agents() {
  const { agents } = useAppProvider();
  const [agentsList, setAgentsList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await agents.getAgents();
        setAgentsList(data);
      } catch(e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchAgents();
  }, [agents]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center text-[var(--color-text-muted)]">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 rounded-full border-4 border-[var(--color-bg-subtle)] border-t-[var(--color-brand-accent)] animate-spin"></div>
          <p className="text-sm font-medium">Loading Agents...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col gap-2 border-b border-[var(--color-border-primary)] pb-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-text-primary)]">AI Agents</h1>
        </div>
        <p className="text-[var(--color-text-tertiary)] text-lg">Your autonomous marketing team. Each agent specializes in a core marketing capability.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {agentsList.map((agent) => (
          <Card key={agent.id} className="flex flex-col hover:border-[var(--color-brand-accent)] transition-colors group cursor-pointer relative overflow-hidden">
            <Link href={`/app/agents/${agent.id}`} className="absolute inset-0 z-10" aria-label={`View ${agent.name} details`} />
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-[var(--color-brand-accent-subtle)] to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-bl-full pointer-events-none"></div>
            <CardHeader className="flex flex-row items-start justify-between pb-4 border-b border-[var(--color-border-primary)]">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-[var(--color-bg-subtle)] rounded-lg text-[var(--color-brand-accent)] border border-[var(--color-border-primary)] group-hover:border-[var(--color-brand-accent)] group-hover:bg-[var(--color-brand-accent)] group-hover:text-white transition-colors relative z-20">
                  <Bot className="h-6 w-6" />
                </div>
                <div>
                  <CardTitle className="text-lg text-[var(--color-text-primary)]">{agent.name}</CardTitle>
                </div>
              </div>
              <Badge className="relative z-20 text-[10px] uppercase tracking-wider" variant={agent.status === 'ACTIVE' ? 'success' : agent.status === 'WAITING' ? 'warning' : 'secondary'}>
                {agent.status || "IDLE"}
              </Badge>
            </CardHeader>
            <CardContent className="pt-4 flex-1 flex flex-col justify-between relative z-20 space-y-6">
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">{agent.description}</p>
              
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {agent.capabilities?.slice(0, 3).map((cap: string, i: number) => (
                    <span key={i} className="text-[10px] uppercase tracking-wider bg-[var(--color-bg-subtle)] text-[var(--color-text-tertiary)] px-2 py-1 rounded border border-[var(--color-border-primary)]">
                      {cap}
                    </span>
                  ))}
                  {agent.capabilities?.length > 3 && (
                    <span className="text-[10px] uppercase tracking-wider bg-[var(--color-bg-subtle)] text-[var(--color-text-tertiary)] px-2 py-1 rounded border border-[var(--color-border-primary)]">
                      +{agent.capabilities.length - 3} more
                    </span>
                  )}
                </div>
                <div className="flex items-center justify-between text-xs font-medium pt-2 border-t border-[var(--color-border-primary)]">
                  <span className="text-[var(--color-text-muted)]">{agent.capabilities?.length || 0} capabilities active</span>
                  <span className="text-[var(--color-brand-accent)] group-hover:translate-x-1 transition-transform inline-block">Configure &rarr;</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
