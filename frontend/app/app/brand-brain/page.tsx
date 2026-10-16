"use client"
import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAppProvider } from '@/lib/providers'
import { ApiClient } from '@/lib/api/client'
import { RefreshCw, Sparkles, Plus, Edit2, Upload, FileText } from 'lucide-react'

export default function BrandBrain() {
  const { brandBrain, auth } = useAppProvider()
  const { activeBrand } = auth
  const [context, setContext] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  // Modal states
  const [activeModal, setActiveModal] = useState<string | null>(null)
  const [formData, setFormData] = useState<any>({})
  const [saving, setSaving] = useState(false)

  const fetchContext = async () => {
    try {
      setLoading(true)
      const data = await brandBrain.getContext()
      setContext(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchContext()
  }, [brandBrain, activeBrand?.id])

  const openModal = (type: string, initialData: any = {}) => {
    setFormData(initialData)
    setActiveModal(type)
  }

  const closeModal = () => {
    setActiveModal(null)
    setFormData({})
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      if (activeModal === 'overview') {
        await ApiClient.patch(`/api/brands/${context?.brand?.id}`, formData)
      } else if (activeModal === 'voice') {
        await brandBrain.updateVoice(formData)
      } else if (activeModal === 'positioning') {
        await brandBrain.updatePositioning(formData)
      } else if (activeModal === 'audience') {
        await brandBrain.addAudience(formData)
      } else if (activeModal === 'product') {
        await brandBrain.addProduct(formData)
      } else if (activeModal === 'competitor') {
        await brandBrain.addCompetitor(formData)
      } else if (activeModal === 'goal') {
        await brandBrain.addGoal(formData)
      }
      closeModal()
      await fetchContext()
    } catch (err: any) {
      alert('Save failed: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading && !context) {
    return (
      <div className="h-full flex items-center justify-center text-[#A9A4A0]">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-4 border-[#242222] border-t-[#8F0028] animate-spin"></div>
          <p className="text-sm font-medium">Loading Brand Brain...</p>
        </div>
      </div>
    )
  }

  const b = context?.brand || {}
  const voice = context?.voice || {}
  const positioning = context?.positioning || {}
  const strategy = context?.strategy || {}
  const audiences = context?.audiences || []
  const products = context?.products || []
  const goals = context?.goals || []
  const competitors = context?.competitors || []
  const documents = context?.documents || []

  return (
    <div className="space-y-8 max-w-7xl mx-auto p-6 w-full text-[#F5F3F1]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#373333] pb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-[#F5F3F1]">Brand Brain</h1>
            <Badge variant="outline" className="bg-[#242222] border-[#373333] text-[#00A650] text-xs">
              Live & Synced
            </Badge>
          </div>
          <p className="text-[#A9A4A0] text-sm mt-1">
            The central intelligence layer your AI marketing agents use to understand your voice, positioning, and products.
          </p>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={fetchContext} 
          disabled={loading}
          className="border-[#373333] text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Context
        </Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        
        {/* Brand Overview */}
        <Card className="flex flex-col bg-[#1C1A1A] border-[#373333]">
          <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-[#373333]">
            <CardTitle className="text-base text-[#F5F3F1]">Business Overview</CardTitle>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => openModal('overview', { ...b })}
              className="h-7 text-xs text-[#8F0028] hover:text-white hover:bg-[#8F0028]"
            >
              <Edit2 className="w-3 h-3 mr-1" /> Edit
            </Button>
          </CardHeader>
          <CardContent className="space-y-3 text-sm flex-1 flex flex-col pt-4">
            <div className="space-y-2.5 flex-1">
              {[
                ['Name', b.name],
                ['Industry', b.industry],
                ['Category', b.category],
                ['Location', b.location],
                ['Mission', b.mission],
                ['Vision', b.vision],
                ['Tagline', b.tagline]
              ].map(([key, value]) => (
                <div key={key as string} className="text-xs">
                  <span className="font-semibold text-[#A9A4A0]">{key}: </span> 
                  <span className={value ? "text-[#F5F3F1]" : "text-[#737373] italic"}>
                    {value || "Not defined"}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        {/* Brand Voice */}
        <Card className="flex flex-col bg-[#1C1A1A] border-[#373333]">
          <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-[#373333]">
            <CardTitle className="text-base text-[#F5F3F1]">Brand Voice</CardTitle>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => openModal('voice', { ...voice })}
              className="h-7 text-xs text-[#8F0028] hover:text-white hover:bg-[#8F0028]"
            >
              <Edit2 className="w-3 h-3 mr-1" /> Edit
            </Button>
          </CardHeader>
          <CardContent className="space-y-4 text-sm flex-1 flex flex-col pt-4">
            <div className="flex-1 space-y-4">
              <div className="flex gap-2 flex-wrap">
                {voice.tone ? <Badge className="bg-[#242222] border-[#373333] text-[#F5F3F1]">{voice.tone}</Badge> : <Badge variant="outline" className="text-[#737373]">No tone specified</Badge>}
                {voice.personality && <Badge className="bg-[#242222] border-[#373333] text-[#00A650]">{voice.personality}</Badge>}
              </div>
              <div className="space-y-2 text-xs">
                <div>
                  <span className="font-semibold text-[#A9A4A0]">Writing Style: </span> 
                  <span className={voice.writing_style ? "text-[#F5F3F1]" : "text-[#737373] italic"}>
                    {voice.writing_style || "Not defined"}
                  </span>
                </div>
                <div>
                  <span className="font-semibold text-[#A9A4A0]">Formality: </span> 
                  <span className={voice.formality ? "text-[#F5F3F1]" : "text-[#737373] italic"}>
                    {voice.formality || "Not defined"}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Positioning */}
        <Card className="flex flex-col bg-[#1C1A1A] border-[#373333]">
          <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-[#373333]">
            <CardTitle className="text-base text-[#F5F3F1]">Positioning & UVP</CardTitle>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => openModal('positioning', { ...positioning })}
              className="h-7 text-xs text-[#8F0028] hover:text-white hover:bg-[#8F0028]"
            >
              <Edit2 className="w-3 h-3 mr-1" /> Edit
            </Button>
          </CardHeader>
          <CardContent className="space-y-4 text-xs flex-1 flex flex-col pt-4">
            <div className="flex-1 space-y-3">
              <div>
                <span className="font-semibold text-[#A9A4A0] block mb-1">Positioning Statement</span> 
                <span className={positioning.positioning_statement ? "text-[#F5F3F1] leading-relaxed" : "text-[#737373] italic"}>
                  {positioning.positioning_statement || "Not defined yet."}
                </span>
              </div>
              <div>
                <span className="font-semibold text-[#A9A4A0] block mb-1">Unique Value Proposition (UVP)</span> 
                <span className={positioning.unique_value_proposition ? "text-[#F5F3F1] leading-relaxed" : "text-[#737373] italic"}>
                  {positioning.unique_value_proposition || "Not defined yet."}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Audiences */}
        <Card className="flex flex-col bg-[#1C1A1A] border-[#373333]">
          <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-[#373333]">
            <div className="flex items-center gap-2">
              <CardTitle className="text-base text-[#F5F3F1]">Audiences</CardTitle>
              <Badge variant="outline" className="bg-[#242222] border-[#373333] text-[#A9A4A0] text-[10px]">{audiences.length}</Badge>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => openModal('audience')}
              className="h-7 text-xs text-[#8F0028] hover:text-white hover:bg-[#8F0028]"
            >
              <Plus className="w-3 h-3 mr-1" /> Add
            </Button>
          </CardHeader>
          <CardContent className="space-y-3 text-xs flex-1 flex flex-col pt-4">
            <div className="flex-1 space-y-2.5">
              {audiences.length > 0 ? audiences.map((aud: any) => (
                <div key={aud.id} className="p-3 border border-[#373333] rounded-lg bg-[#242222]">
                  <div className="font-semibold text-[#F5F3F1]">{aud.name}</div>
                  <div className="text-[#A9A4A0] mt-1 text-[11px] leading-relaxed">{aud.description}</div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center h-full py-6 text-center text-[#737373] border border-dashed border-[#373333] rounded-lg">
                  <span className="italic">No audiences defined</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Products */}
        <Card className="flex flex-col bg-[#1C1A1A] border-[#373333]">
          <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-[#373333]">
            <div className="flex items-center gap-2">
              <CardTitle className="text-base text-[#F5F3F1]">Products / Services</CardTitle>
              <Badge variant="outline" className="bg-[#242222] border-[#373333] text-[#A9A4A0] text-[10px]">{products.length}</Badge>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => openModal('product')}
              className="h-7 text-xs text-[#8F0028] hover:text-white hover:bg-[#8F0028]"
            >
              <Plus className="w-3 h-3 mr-1" /> Add
            </Button>
          </CardHeader>
          <CardContent className="space-y-3 text-xs flex-1 flex flex-col pt-4">
            <div className="flex-1 space-y-2.5">
              {products.length > 0 ? products.map((prod: any) => (
                <div key={prod.id} className="p-3 border border-[#373333] rounded-lg bg-[#242222]">
                  <div className="flex items-start justify-between gap-2">
                    <div className="font-semibold text-[#F5F3F1]">{prod.name}</div>
                    {prod.price && <span className="text-[10px] font-semibold text-[#00A650] bg-[#00A650]/10 px-2 py-0.5 rounded">{prod.price}</span>}
                  </div>
                  <div className="text-[#A9A4A0] mt-1 text-[11px] leading-relaxed">{prod.description}</div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center h-full py-6 text-center text-[#737373] border border-dashed border-[#373333] rounded-lg">
                  <span className="italic">No products defined</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Competitors */}
        <Card className="flex flex-col bg-[#1C1A1A] border-[#373333]">
          <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-[#373333]">
            <div className="flex items-center gap-2">
              <CardTitle className="text-base text-[#F5F3F1]">Competitors</CardTitle>
              <Badge variant="outline" className="bg-[#242222] border-[#373333] text-[#A9A4A0] text-[10px]">{competitors.length}</Badge>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => openModal('competitor')}
              className="h-7 text-xs text-[#8F0028] hover:text-white hover:bg-[#8F0028]"
            >
              <Plus className="w-3 h-3 mr-1" /> Add
            </Button>
          </CardHeader>
          <CardContent className="space-y-3 text-xs flex-1 flex flex-col pt-4">
            <div className="flex-1 space-y-2.5">
              {competitors.length > 0 ? competitors.map((comp: any) => (
                <div key={comp.id} className="p-3 border border-[#373333] rounded-lg bg-[#242222]">
                  <div className="font-semibold text-[#F5F3F1]">{comp.name}</div>
                  <div className="text-[#A9A4A0] mt-1 text-[11px] leading-relaxed line-clamp-2">
                    <span className="font-medium text-red-400">Weakness: </span>{comp.weaknesses || "None recorded"}
                  </div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center h-full py-6 text-center text-[#737373] border border-dashed border-[#373333] rounded-lg px-4">
                  <span className="italic">No competitors added</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Goals */}
        <Card className="flex flex-col bg-[#1C1A1A] border-[#373333]">
          <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-[#373333]">
            <div className="flex items-center gap-2">
              <CardTitle className="text-base text-[#F5F3F1]">Goals</CardTitle>
              <Badge variant="outline" className="bg-[#242222] border-[#373333] text-[#A9A4A0] text-[10px]">{goals.length}</Badge>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => openModal('goal')}
              className="h-7 text-xs text-[#8F0028] hover:text-white hover:bg-[#8F0028]"
            >
              <Plus className="w-3 h-3 mr-1" /> Add
            </Button>
          </CardHeader>
          <CardContent className="space-y-3 text-xs flex-1 flex flex-col pt-4">
            <div className="flex-1 space-y-2.5">
              {goals.length > 0 ? goals.map((goal: any) => (
                <div key={goal.id} className="p-3 border border-[#373333] rounded-lg bg-[#242222] flex justify-between items-center gap-2">
                  <div className="min-w-0">
                    <div className="font-semibold text-[#F5F3F1] truncate">{goal.goal}</div>
                    <div className="text-[#A9A4A0] text-[11px] mt-0.5">Target: {goal.target_value}</div>
                  </div>
                  <Badge variant="outline" className="border-[#373333] text-[#A9A4A0] text-[10px] shrink-0">
                    {goal.current_value || 'Active'}
                  </Badge>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center h-full py-6 text-center text-[#737373] border border-dashed border-[#373333] rounded-lg">
                  <span className="italic">No goals defined</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

      </div>

      {/* Universal Dynamic Modal Dialog */}
      {activeModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#1C1A1A] border border-[#373333] rounded-2xl max-w-md w-full p-6 space-y-5 shadow-2xl">
            <div className="flex justify-between items-center border-b border-[#373333] pb-3">
              <h2 className="text-lg font-bold text-[#F5F3F1] capitalize">
                {activeModal.startsWith('edit') ? activeModal : `Add ${activeModal}`}
              </h2>
              <button onClick={closeModal} className="text-[#A9A4A0] hover:text-[#F5F3F1]">✕</button>
            </div>
            
            <form onSubmit={handleSave} className="space-y-4">
              {activeModal === 'overview' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Brand Name</label>
                    <Input 
                      value={formData.name || ''} 
                      onChange={e => setFormData({ ...formData, name: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Industry</label>
                    <Input 
                      value={formData.industry || ''} 
                      onChange={e => setFormData({ ...formData, industry: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Tagline</label>
                    <Input 
                      value={formData.tagline || ''} 
                      onChange={e => setFormData({ ...formData, tagline: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                </>
              )}

              {activeModal === 'voice' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Tone</label>
                    <Input 
                      placeholder="e.g. Authoritative, direct, encouraging"
                      value={formData.tone || ''} 
                      onChange={e => setFormData({ ...formData, tone: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Writing Style</label>
                    <Input 
                      placeholder="e.g. Data-driven, concise, narrative"
                      value={formData.writing_style || ''} 
                      onChange={e => setFormData({ ...formData, writing_style: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                </>
              )}

              {activeModal === 'positioning' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Positioning Statement</label>
                    <textarea 
                      rows={3}
                      value={formData.positioning_statement || ''} 
                      onChange={e => setFormData({ ...formData, positioning_statement: e.target.value })}
                      className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-xs text-[#F5F3F1] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Unique Value Proposition</label>
                    <textarea 
                      rows={2}
                      value={formData.unique_value_proposition || ''} 
                      onChange={e => setFormData({ ...formData, unique_value_proposition: e.target.value })}
                      className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-xs text-[#F5F3F1] focus:outline-none"
                    />
                  </div>
                </>
              )}

              {activeModal === 'audience' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Audience Name *</label>
                    <Input 
                      required
                      placeholder="e.g. SMB Founders"
                      value={formData.name || ''} 
                      onChange={e => setFormData({ ...formData, name: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Description & Pain Points</label>
                    <textarea 
                      rows={3}
                      placeholder="Demographics, key challenges, motivations..."
                      value={formData.description || ''} 
                      onChange={e => setFormData({ ...formData, description: e.target.value })}
                      className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-xs text-[#F5F3F1] focus:outline-none"
                    />
                  </div>
                </>
              )}

              {activeModal === 'product' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Product / Service Name *</label>
                    <Input 
                      required
                      placeholder="e.g. Enterprise SEO Audit"
                      value={formData.name || ''} 
                      onChange={e => setFormData({ ...formData, name: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Pricing (Optional)</label>
                    <Input 
                      placeholder="e.g. ₹49,000 / month"
                      value={formData.price || ''} 
                      onChange={e => setFormData({ ...formData, price: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Description</label>
                    <textarea 
                      rows={2}
                      placeholder="Key benefits and target customer..."
                      value={formData.description || ''} 
                      onChange={e => setFormData({ ...formData, description: e.target.value })}
                      className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-xs text-[#F5F3F1] focus:outline-none"
                    />
                  </div>
                </>
              )}

              {activeModal === 'competitor' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Competitor Name *</label>
                    <Input 
                      required
                      placeholder="e.g. Market Rival Ltd"
                      value={formData.name || ''} 
                      onChange={e => setFormData({ ...formData, name: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Known Weakness / Gap</label>
                    <Input 
                      placeholder="e.g. Slow delivery, weak technical content"
                      value={formData.weaknesses || ''} 
                      onChange={e => setFormData({ ...formData, weaknesses: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                </>
              )}

              {activeModal === 'goal' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Marketing Goal *</label>
                    <Input 
                      required
                      placeholder="e.g. Reach ₹50L Annual Recurring Revenue"
                      value={formData.goal || ''} 
                      onChange={e => setFormData({ ...formData, goal: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[#A9A4A0] uppercase tracking-wider mb-1">Target Metric / Value</label>
                    <Input 
                      placeholder="e.g. ₹5,000,000"
                      value={formData.target_value || ''} 
                      onChange={e => setFormData({ ...formData, target_value: e.target.value })}
                      className="bg-[#242222] border-[#373333] text-sm"
                    />
                  </div>
                </>
              )}

              <div className="flex justify-end gap-3 pt-3 border-t border-[#373333]">
                <Button type="button" variant="outline" onClick={closeModal} className="border-[#373333] text-[#A9A4A0]">
                  Cancel
                </Button>
                <Button type="submit" disabled={saving} className="bg-[#8F0028] hover:bg-[#A8002F] text-white">
                  {saving ? 'Saving...' : 'Save to Brand Brain'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
