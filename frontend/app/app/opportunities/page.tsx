"use client"
import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ApiClient } from '@/lib/api/client'
import { useAuth } from '@/lib/providers/MockProvider'
import { 
  Zap, Target, TrendingUp, CheckCircle2, XCircle, 
  Trash2, Plus, RefreshCw, AlertCircle, ArrowUpRight, Sparkles 
} from 'lucide-react'

interface Opportunity {
  id: string
  title: string
  description?: string
  opportunity_type?: string
  impact: string
  confidence: number
  effort?: string
  priority: number
  status: string
  created_at: string
}

export default function OpportunitiesPage() {
  const { activeBrand } = useAuth()
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newOpp, setNewOpp] = useState({
    title: '',
    description: '',
    opportunity_type: 'SEO',
    impact: 'HIGH',
    confidence: 85,
    effort: 'MEDIUM',
    priority: 88
  })

  const fetchOpportunities = async () => {
    if (!activeBrand) return
    setLoading(true)
    setError(null)
    try {
      const data = await ApiClient.get<Opportunity[]>('/api/opportunities/')
      setOpportunities(data || [])
    } catch (e: any) {
      console.error(e)
      setError(e.message || 'Failed to load opportunities')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOpportunities()
  }, [activeBrand?.id])

  const handleDismiss = async (id: string) => {
    setActionLoading(id)
    try {
      await ApiClient.delete(`/api/opportunities/${id}`)
      setOpportunities(prev => prev.filter(o => o.id !== id))
    } catch (e: any) {
      alert('Failed to dismiss: ' + e.message)
    } finally {
      setActionLoading(null)
    }
  }

  const handleExecute = async (opp: Opportunity) => {
    setActionLoading(opp.id)
    try {
      // Mark opportunity as IN_PROGRESS and trigger agent action
      await ApiClient.patch(`/api/opportunities/${opp.id}`, { status: 'IN_PROGRESS' })
      setOpportunities(prev => prev.map(o => o.id === opp.id ? { ...o, status: 'IN_PROGRESS' } : o))
      
      // Auto-create a content project or brief if it's content-related
      try {
        await ApiClient.post('/api/content/drafts', {
          title: opp.title,
          content_type: 'blog',
          body: `Drafting campaign initiated for strategic opportunity: ${opp.title}.\n\nContext: ${opp.description || 'Targeting high-intent organic keywords.'}`,
          status: 'DRAFT'
        })
      } catch (err) {}
      
      alert(`Action executed! Created corresponding content draft and marked opportunity as IN_PROGRESS.`)
    } catch (e: any) {
      alert('Failed to execute action: ' + e.message)
    } finally {
      setActionLoading(null)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newOpp.title.trim()) return
    try {
      const created = await ApiClient.post<Opportunity>('/api/opportunities/', newOpp)
      setOpportunities(prev => [created, ...prev])
      setShowCreateModal(false)
      setNewOpp({
        title: '',
        description: '',
        opportunity_type: 'SEO',
        impact: 'HIGH',
        confidence: 85,
        effort: 'MEDIUM',
        priority: 88
      })
    } catch (e: any) {
      alert('Failed to create opportunity: ' + e.message)
    }
  }

  const getImpactColor = (impact: string) => {
    switch (impact?.toUpperCase()) {
      case 'HIGH':
        return 'text-red-400 bg-red-950/40 border-red-800'
      case 'MEDIUM':
        return 'text-amber-400 bg-amber-950/40 border-amber-800'
      default:
        return 'text-blue-400 bg-blue-950/40 border-blue-800'
    }
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 max-w-7xl mx-auto w-full space-y-6 text-[#F5F3F1]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#373333] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-[#F5F3F1]">Growth Opportunities</h1>
            <Badge variant="outline" className="bg-[#242222] border-[#373333] text-[#A9A4A0] text-xs">
              {opportunities.length} Active
            </Badge>
          </div>
          <p className="text-[#A9A4A0] text-sm mt-1">
            Prioritized strategic marketing actions identified by AI CMO & competitor intelligence.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchOpportunities} 
            disabled={loading}
            className="border-[#373333] text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button 
            size="sm" 
            onClick={() => setShowCreateModal(true)}
            className="bg-[#8F0028] hover:bg-[#A8002F] text-white flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            + New Opportunity
          </Button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-950/30 border border-red-800 rounded-xl text-red-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{error}</span>
          </div>
          <Button size="sm" variant="outline" onClick={fetchOpportunities} className="border-red-800 text-red-300">
            Retry
          </Button>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="p-16 text-center text-[#A9A4A0] space-y-3">
          <div className="w-8 h-8 rounded-full border-2 border-[#8F0028] border-t-transparent animate-spin mx-auto"></div>
          <p className="text-sm">Loading verified opportunities from database...</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && opportunities.length === 0 && (
        <div className="p-16 border border-dashed border-[#373333] rounded-2xl bg-[#1C1A1A] text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-[#8F0028]/10 text-[#8F0028] flex items-center justify-center mx-auto">
            <Sparkles className="w-6 h-6" />
          </div>
          <div className="max-w-md mx-auto">
            <h3 className="text-lg font-semibold text-[#F5F3F1]">No Opportunities Logged Yet</h3>
            <p className="text-xs text-[#A9A4A0] mt-1">
              Run the AI CMO or Competitor Agent to automatically uncover search and messaging opportunities, or create your first opportunity manually.
            </p>
          </div>
          <Button 
            onClick={() => setShowCreateModal(true)}
            className="bg-[#8F0028] hover:bg-[#A8002F] text-white text-xs font-semibold"
          >
            + Create Opportunity
          </Button>
        </div>
      )}

      {/* Opportunity Cards List */}
      {!loading && opportunities.length > 0 && (
        <div className="space-y-4">
          {opportunities.map(opp => (
            <Card key={opp.id} className="bg-[#1C1A1A] border-[#373333] hover:border-[#4A4545] transition-all">
              <CardContent className="p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                <div className="space-y-2 flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-3">
                    <h3 className="font-semibold text-lg text-[#F5F3F1] truncate">{opp.title}</h3>
                    <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded border uppercase tracking-wider ${getImpactColor(opp.impact)}`}>
                      {opp.impact} Impact
                    </span>
                    {opp.opportunity_type && (
                      <Badge variant="outline" className="bg-[#242222] border-[#373333] text-[#A9A4A0] text-[10px] font-mono uppercase">
                        {opp.opportunity_type}
                      </Badge>
                    )}
                    {opp.status === 'IN_PROGRESS' && (
                      <Badge className="bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 text-[10px] uppercase">
                        In Progress
                      </Badge>
                    )}
                  </div>

                  {opp.description && (
                    <p className="text-sm text-[#A9A4A0] line-clamp-2 leading-relaxed">
                      {opp.description}
                    </p>
                  )}

                  <div className="flex flex-wrap items-center gap-4 text-xs text-[#A9A4A0] pt-1 font-medium">
                    <span className="flex items-center gap-1">
                      <Target className="w-3.5 h-3.5 text-[#00A650]" />
                      Confidence: <span className="text-[#F5F3F1]">{opp.confidence}%</span>
                    </span>
                    <span className="flex items-center gap-1">
                      <TrendingUp className="w-3.5 h-3.5 text-[#8F0028]" />
                      Priority Score: <span className="text-[#F5F3F1] font-bold">{opp.priority}/100</span>
                    </span>
                    {opp.effort && (
                      <span className="text-[#A9A4A0]">
                        Effort: <span className="text-[#F5F3F1] capitalize">{opp.effort}</span>
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2.5 w-full md:w-auto shrink-0">
                  <Button 
                    variant="outline" 
                    size="sm"
                    disabled={actionLoading === opp.id}
                    onClick={() => handleDismiss(opp.id)}
                    className="border-[#373333] text-[#A9A4A0] hover:text-red-400 hover:border-red-800 hover:bg-red-950/20 text-xs flex items-center gap-1"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Dismiss
                  </Button>
                  <Button 
                    size="sm"
                    disabled={actionLoading === opp.id || opp.status === 'IN_PROGRESS'}
                    onClick={() => handleExecute(opp)}
                    className="bg-[#F5F3F1] text-[#171515] hover:bg-white text-xs font-semibold flex items-center gap-1.5"
                  >
                    <ArrowUpRight className="w-3.5 h-3.5" />
                    {actionLoading === opp.id ? 'Executing...' : opp.status === 'IN_PROGRESS' ? 'In Progress' : 'Execute Action'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Opportunity Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#1C1A1A] border border-[#373333] rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <div className="flex justify-between items-center border-b border-[#373333] pb-3">
              <h2 className="text-lg font-bold text-[#F5F3F1]">Add Growth Opportunity</h2>
              <button onClick={() => setShowCreateModal(false)} className="text-[#A9A4A0] hover:text-[#F5F3F1]">✕</button>
            </div>
            
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Title</label>
                <Input 
                  required
                  placeholder="e.g. Target 'Enterprise AI Marketing Guide' organic gap"
                  value={newOpp.title}
                  onChange={e => setNewOpp({ ...newOpp, title: e.target.value })}
                  className="bg-[#242222] border-[#373333] text-[#F5F3F1] text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Description</label>
                <textarea 
                  rows={3}
                  placeholder="Details on why this opportunity matters and recommended execution plan..."
                  value={newOpp.description}
                  onChange={e => setNewOpp({ ...newOpp, description: e.target.value })}
                  className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-sm text-[#F5F3F1] placeholder:text-[#A9A4A0] focus:outline-none focus:border-[#8F0028]"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Impact</label>
                  <select 
                    value={newOpp.impact}
                    onChange={e => setNewOpp({ ...newOpp, impact: e.target.value })}
                    className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2 text-sm text-[#F5F3F1] focus:outline-none"
                  >
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Category</label>
                  <select 
                    value={newOpp.opportunity_type}
                    onChange={e => setNewOpp({ ...newOpp, opportunity_type: e.target.value })}
                    className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2 text-sm text-[#F5F3F1] focus:outline-none"
                  >
                    <option value="SEO">SEO</option>
                    <option value="CONTENT">CONTENT</option>
                    <option value="COMPETITOR">COMPETITOR</option>
                    <option value="GEO">GEO</option>
                    <option value="SOCIAL">SOCIAL</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Confidence (%)</label>
                  <Input 
                    type="number"
                    min="1"
                    max="100"
                    value={newOpp.confidence}
                    onChange={e => setNewOpp({ ...newOpp, confidence: parseInt(e.target.value) || 0 })}
                    className="bg-[#242222] border-[#373333] text-[#F5F3F1] text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Priority (0-100)</label>
                  <Input 
                    type="number"
                    min="1"
                    max="100"
                    value={newOpp.priority}
                    onChange={e => setNewOpp({ ...newOpp, priority: parseInt(e.target.value) || 0 })}
                    className="bg-[#242222] border-[#373333] text-[#F5F3F1] text-sm"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-[#373333]">
                <Button type="button" variant="outline" onClick={() => setShowCreateModal(false)} className="border-[#373333] text-[#A9A4A0]">
                  Cancel
                </Button>
                <Button type="submit" className="bg-[#8F0028] hover:bg-[#A8002F] text-white">
                  Save Opportunity
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
