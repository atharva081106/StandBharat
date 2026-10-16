"use client"
import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ApiClient } from '@/lib/api/client'
import { useAuth } from '@/lib/providers/MockProvider'
import { 
  ShieldAlert, Plus, RefreshCw, AlertCircle, Globe, 
  Trash2, ExternalLink, Zap, Swords, Target, Eye
} from 'lucide-react'

interface Competitor {
  id: string
  brand_id: string
  name: string
  description?: string | null
  website_url?: string | null
  strengths?: string | null
  weaknesses?: string | null
  positioning?: string | null
  notes?: string | null
  created_at?: string
}

export default function CompetitorsPage() {
  const { activeBrand } = useAuth()
  const [competitors, setCompetitors] = useState<Competitor[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const [form, setForm] = useState({
    name: '',
    website_url: '',
    description: '',
    strengths: '',
    weaknesses: '',
    positioning: ''
  })

  const fetchCompetitors = async () => {
    if (!activeBrand) return
    setLoading(true)
    setError(null)
    try {
      const data = await ApiClient.get<Competitor[]>('/api/brand-brain/competitors')
      setCompetitors(data || [])
    } catch (err: any) {
      console.error('Failed to load competitors:', err)
      setError(err.message || 'Failed to load competitors')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCompetitors()
  }, [activeBrand?.id])

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to remove this competitor?')) return
    setActionLoading(id)
    try {
      await ApiClient.delete(`/api/brand-brain/competitors/${id}`)
      setCompetitors(prev => prev.filter(c => c.id !== id))
    } catch (err: any) {
      alert('Failed to delete competitor: ' + err.message)
    } finally {
      setActionLoading(null)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name.trim()) return
    setSaving(true)
    try {
      const created = await ApiClient.post<Competitor>('/api/brand-brain/competitors', form)
      setCompetitors(prev => [...prev, created])
      setShowModal(false)
      setForm({ name: '', website_url: '', description: '', strengths: '', weaknesses: '', positioning: '' })
    } catch (err: any) {
      alert('Failed to add competitor: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 max-w-7xl mx-auto w-full space-y-6 text-[#F5F3F1]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#373333] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-[#F5F3F1]">Competitor Landscape</h1>
            <Badge variant="outline" className="bg-[#242222] border-[#373333] text-[#A9A4A0] text-xs">
              {competitors.length} Tracked
            </Badge>
          </div>
          <p className="text-[#A9A4A0] text-sm mt-1">
            Analyze market rivals, detect messaging vulnerabilities, and uncover keyword/positioning gaps.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchCompetitors} 
            disabled={loading}
            className="border-[#373333] text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button 
            size="sm" 
            onClick={() => setShowModal(true)}
            className="bg-[#8F0028] hover:bg-[#A8002F] text-white flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            + Add Competitor
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
          <Button size="sm" variant="outline" onClick={fetchCompetitors} className="border-red-800 text-red-300">
            Retry
          </Button>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="p-16 text-center text-[#A9A4A0] space-y-3">
          <div className="w-8 h-8 rounded-full border-2 border-[#8F0028] border-t-transparent animate-spin mx-auto"></div>
          <p className="text-sm">Loading competitor profiles from PostgreSQL...</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && competitors.length === 0 && (
        <div className="p-16 border border-dashed border-[#373333] rounded-2xl bg-[#1C1A1A] text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-[#8F0028]/10 text-[#8F0028] flex items-center justify-center mx-auto">
            <Swords className="w-6 h-6" />
          </div>
          <div className="max-w-md mx-auto">
            <h3 className="text-lg font-semibold text-[#F5F3F1]">No Competitors Added Yet</h3>
            <p className="text-xs text-[#A9A4A0] mt-1">
              Add your key direct and indirect competitors so the AI CMO can analyze market positioning and formulate defensive strategies.
            </p>
          </div>
          <Button 
            onClick={() => setShowModal(true)}
            className="bg-[#8F0028] hover:bg-[#A8002F] text-white text-xs font-semibold"
          >
            + Add Competitor
          </Button>
        </div>
      )}

      {/* Competitors Grid */}
      {!loading && competitors.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {competitors.map(comp => (
            <Card key={comp.id} className="bg-[#1C1A1A] border-[#373333] hover:border-[#4A4545] transition-all flex flex-col justify-between">
              <CardHeader className="pb-3 border-b border-[#373333]">
                <div className="flex justify-between items-start gap-2">
                  <div>
                    <CardTitle className="text-lg text-[#F5F3F1] font-bold">
                      {comp.name}
                    </CardTitle>
                    {comp.website_url && (
                      <a 
                        href={comp.website_url.startsWith('http') ? comp.website_url : `https://${comp.website_url}`}
                        target="_blank" 
                        rel="noreferrer"
                        className="text-xs text-[#00A650] hover:underline flex items-center gap-1 mt-0.5"
                      >
                        <Globe className="w-3 h-3" />
                        {comp.website_url.replace(/^https?:\/\//, '')}
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    )}
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    disabled={actionLoading === comp.id}
                    onClick={() => handleDelete(comp.id)}
                    className="h-8 w-8 p-0 text-[#A9A4A0] hover:text-red-400 hover:bg-red-950/20"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="pt-4 space-y-4 flex-1 flex flex-col justify-between">
                {comp.description && (
                  <p className="text-xs text-[#A9A4A0] leading-relaxed line-clamp-3">
                    {comp.description}
                  </p>
                )}

                <div className="space-y-3 pt-2 border-t border-[#373333] text-xs">
                  {comp.positioning && (
                    <div>
                      <span className="font-semibold text-[#A9A4A0] block text-[10px] uppercase tracking-wider mb-0.5">Positioning</span>
                      <span className="text-[#F5F3F1]">{comp.positioning}</span>
                    </div>
                  )}

                  {comp.strengths && (
                    <div>
                      <span className="font-semibold text-[#00A650] block text-[10px] uppercase tracking-wider mb-0.5">Strengths</span>
                      <span className="text-[#A9A4A0]">{comp.strengths}</span>
                    </div>
                  )}

                  {comp.weaknesses && (
                    <div>
                      <span className="font-semibold text-red-400 block text-[10px] uppercase tracking-wider mb-0.5">Weaknesses / Gaps</span>
                      <span className="text-[#A9A4A0]">{comp.weaknesses}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Competitor Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#1C1A1A] border border-[#373333] rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <div className="flex justify-between items-center border-b border-[#373333] pb-3">
              <h2 className="text-lg font-bold text-[#F5F3F1]">Add Competitor Profile</h2>
              <button onClick={() => setShowModal(false)} className="text-[#A9A4A0] hover:text-[#F5F3F1]">✕</button>
            </div>
            
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Competitor Name *</label>
                  <Input 
                    required
                    placeholder="e.g. Acme Brands"
                    value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })}
                    className="bg-[#242222] border-[#373333] text-[#F5F3F1] text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Website URL</label>
                  <Input 
                    placeholder="e.g. acme.com"
                    value={form.website_url}
                    onChange={e => setForm({ ...form, website_url: e.target.value })}
                    className="bg-[#242222] border-[#373333] text-[#F5F3F1] text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Market Positioning</label>
                <Input 
                  placeholder="e.g. Low-cost mass-market alternative"
                  value={form.positioning}
                  onChange={e => setForm({ ...form, positioning: e.target.value })}
                  className="bg-[#242222] border-[#373333] text-[#F5F3F1] text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#00A650] uppercase tracking-wider mb-1">Strengths</label>
                  <textarea 
                    rows={2}
                    placeholder="e.g. High domain authority, huge ad budget"
                    value={form.strengths}
                    onChange={e => setForm({ ...form, strengths: e.target.value })}
                    className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-xs text-[#F5F3F1] placeholder:text-[#A9A4A0] focus:outline-none focus:border-[#8F0028]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-red-400 uppercase tracking-wider mb-1">Weaknesses</label>
                  <textarea 
                    rows={2}
                    placeholder="e.g. Slow customer support, generic messaging"
                    value={form.weaknesses}
                    onChange={e => setForm({ ...form, weaknesses: e.target.value })}
                    className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-xs text-[#F5F3F1] placeholder:text-[#A9A4A0] focus:outline-none focus:border-[#8F0028]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Description / Notes</label>
                <textarea 
                  rows={2}
                  placeholder="Additional context about this competitor..."
                  value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })}
                  className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-xs text-[#F5F3F1] placeholder:text-[#A9A4A0] focus:outline-none focus:border-[#8F0028]"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-[#373333]">
                <Button type="button" variant="outline" onClick={() => setShowModal(false)} className="border-[#373333] text-[#A9A4A0]">
                  Cancel
                </Button>
                <Button type="submit" disabled={saving} className="bg-[#8F0028] hover:bg-[#A8002F] text-white">
                  {saving ? 'Saving...' : 'Add Competitor'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
