"use client"
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { MessageSquare, Send } from 'lucide-react'
import { useState } from 'react'
import { useAppProvider } from '@/lib/providers'

export default function AICMO() {
  const { aiCmo } = useAppProvider()
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<{role: 'user'|'ai', text: string}[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const userMessage = input
    setMessages(prev => [...prev, { role: 'user', text: userMessage }])
    setInput('')
    setIsLoading(true)
    
    try {
      const { status, response } = await aiCmo.chat(userMessage)
      if (status === 'SUCCESS') {
        setMessages(prev => [...prev, { role: 'ai', text: response }])
      } else if (status === 'AI_NOT_CONFIGURED') {
        setMessages(prev => [...prev, { role: 'ai', text: "[System]: AI Provider is not configured. Please add an API key." }])
      } else if (status === 'AI_AUTH_ERROR') {
        setMessages(prev => [...prev, { role: 'ai', text: "[System]: AI Provider authentication failed. Please check your API key." }])
      } else {
        setMessages(prev => [...prev, { role: 'ai', text: `[System]: Error processing request (${status}).` }])
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'ai', text: "[System]: Failed to connect to AI CMO." }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="h-[calc(100vh-6rem)] flex gap-6 max-w-[1600px] mx-auto">
      {/* Left Column: Chat Interface */}
      <div className="flex-1 flex flex-col bg-[var(--color-bg-surface)] rounded-xl shadow-sm border border-[var(--color-border-primary)] overflow-hidden">
        <div className="p-4 border-b border-[var(--color-border-primary)] flex justify-between items-center bg-[var(--color-bg-subtle)]">
          <div>
            <h2 className="text-lg font-semibold flex items-center gap-2 text-[var(--color-text-primary)]">
              <MessageSquare className="w-5 h-5 text-[var(--color-brand-accent)]" /> AI CMO
            </h2>
            <p className="text-xs text-[var(--color-text-tertiary)] mt-0.5">Your autonomous marketing strategist.</p>
          </div>
          <div className="flex items-center gap-2 bg-[var(--color-bg-surface)] px-2.5 py-1 rounded-full border border-[var(--color-border-primary)]">
            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
            <span className="text-xs font-semibold text-green-700 tracking-wider">ONLINE</span>
          </div>
        </div>
        
        <div className="flex-1 p-6 overflow-y-auto space-y-6 bg-[var(--color-bg-primary)]">
          <div className="flex flex-col items-end">
             <div className="bg-[var(--color-text-primary)] text-white p-4 rounded-2xl rounded-tr-sm max-w-[85%] shadow-sm">
               <p className="text-sm">What should we focus on this week?</p>
             </div>
          </div>
          
          <div className="flex flex-col items-start">
             <div className="bg-[var(--color-bg-surface)] border border-[var(--color-border-primary)] p-4 rounded-2xl rounded-tl-sm max-w-[85%] shadow-sm">
               <p className="text-sm text-[var(--color-text-primary)] mb-4">Your strongest opportunity is targeting the enterprise segment for AI marketing. I've analyzed our competitor gaps and found several quick wins.</p>
               <Card className="shadow-none border-[var(--color-border-primary)] bg-[var(--color-bg-subtle)]">
                  <div className="p-4 space-y-3">
                    <div className="font-semibold text-sm text-[var(--color-text-primary)]">Target: "Enterprise AI Marketing Automation Guide"</div>
                    <div className="flex gap-4 text-xs font-medium">
                      <span className="text-[var(--color-brand-accent)] bg-[var(--color-brand-accent-subtle)] px-2 py-0.5 rounded">Impact: HIGH</span>
                      <span className="text-[var(--color-text-secondary)] bg-[var(--color-bg-primary)] border border-[var(--color-border-primary)] px-2 py-0.5 rounded">Confidence: 87%</span>
                    </div>
                    <p className="text-xs text-[var(--color-text-tertiary)]">The Growth Agent identified the gap and the Content Strategy Agent has prepared a brief for your review.</p>
                    <Button size="sm" className="w-full mt-2">Review Recommended Action</Button>
                  </div>
               </Card>
             </div>
          </div>
          {messages.map((m, i) => (
            <div key={i} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`p-4 rounded-2xl max-w-[85%] shadow-sm ${m.role === 'user' ? 'bg-[var(--color-text-primary)] text-white rounded-tr-sm' : 'bg-[var(--color-bg-surface)] border border-[var(--color-border-primary)] text-[var(--color-text-primary)] rounded-tl-sm'}`}>
                <p className="text-sm whitespace-pre-wrap">{m.text}</p>
              </div>
            </div>
          ))}
        </div>
        
        <div className="p-4 border-t border-[var(--color-border-primary)] bg-[var(--color-bg-surface)]">
          <div className="flex gap-2 mb-3 overflow-x-auto pb-2 scrollbar-hide">
            {["What's my biggest growth opportunity?", "What should we publish this week?", "Analyze competitor positioning", "What needs my approval?"].map(p => (
              <button key={p} onClick={() => setInput(p)} className="text-xs px-3 py-1.5 rounded-full border border-[var(--color-border-primary)] bg-[var(--color-bg-subtle)] text-[var(--color-text-tertiary)] hover:bg-[var(--color-border-primary)] hover:text-[var(--color-text-primary)] transition-colors whitespace-nowrap font-medium shadow-sm">
                {p}
              </button>
            ))}
          </div>
          <div className="relative flex items-center">
            <Input 
              value={input} 
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask your AI CMO..." 
              className="pr-12 rounded-full bg-[var(--color-bg-subtle)] border-[var(--color-border-primary)] focus-visible:ring-[var(--color-brand-accent)] h-12" 
            />
            <button onClick={handleSend} disabled={isLoading} className="absolute right-2 p-2 bg-[var(--color-brand-accent)] text-white rounded-full hover:bg-[var(--color-brand-accent-hover)] disabled:opacity-50 transition-colors shadow-sm">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Right Column: Context & Actions */}
      <div className="w-[320px] lg:w-[400px] flex-col gap-6 hidden md:flex overflow-y-auto pr-2">
        <div className="space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Current Context</h3>
          
          <Card>
            <div className="p-4 border-b border-[var(--color-border-primary)] bg-[var(--color-bg-subtle)]">
              <p className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Active Workflow</p>
              <p className="text-sm font-medium text-[var(--color-text-primary)]">Q4 Launch Strategy Preparation</p>
            </div>
            <div className="p-4 space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-6 flex flex-col items-center gap-1 shrink-0">
                  <div className="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center"><div className="w-1.5 h-1.5 bg-white rounded-full"></div></div>
                  <div className="w-0.5 h-6 bg-green-200"></div>
                </div>
                <div className="-mt-1">
                  <p className="text-sm font-medium text-[var(--color-text-primary)]">Data Analysis</p>
                  <p className="text-xs text-[var(--color-text-tertiary)]">Completed by Analytics Agent</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 flex flex-col items-center gap-1 shrink-0">
                  <div className="w-4 h-4 rounded-full bg-[var(--color-brand-accent)] flex items-center justify-center animate-pulse"><div className="w-1.5 h-1.5 bg-white rounded-full"></div></div>
                  <div className="w-0.5 h-6 bg-[var(--color-border-primary)]"></div>
                </div>
                <div className="-mt-1">
                  <p className="text-sm font-medium text-[var(--color-brand-accent)]">Content Generation</p>
                  <p className="text-xs text-[var(--color-text-tertiary)]">Writer Agent is drafting post</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 flex flex-col items-center gap-1 shrink-0">
                  <div className="w-4 h-4 rounded-full border-2 border-[var(--color-border-primary)] bg-transparent flex items-center justify-center"></div>
                </div>
                <div className="-mt-1">
                  <p className="text-sm font-medium text-[var(--color-text-muted)]">Human Approval</p>
                  <p className="text-xs text-[var(--color-text-muted)]">Awaiting draft completion</p>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-4 border-b border-[var(--color-border-primary)]">
              <p className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Knowledge Access</p>
              <p className="text-sm font-medium text-[var(--color-text-primary)]">Brand Brain Connections</p>
            </div>
            <div className="p-4 space-y-3">
               <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
                 <div className="h-1.5 w-1.5 rounded-full bg-green-500"></div>
                 Brand Voice & Guidelines
               </div>
               <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
                 <div className="h-1.5 w-1.5 rounded-full bg-green-500"></div>
                 Competitor Landscape
               </div>
               <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
                 <div className="h-1.5 w-1.5 rounded-full bg-amber-500"></div>
                 Revenue Attribution <span className="text-xs text-[var(--color-text-muted)]">(Partial)</span>
               </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
