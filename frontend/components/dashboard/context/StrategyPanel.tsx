"use client"
import { useState, useEffect } from 'react'
import { useAppProvider } from '@/lib/providers'
import { ApiClient } from '@/lib/api/client'
import { FileText, Save, Loader2, AlertCircle } from 'lucide-react'

export function StrategyPanel() {
  const { auth: { activeBrand, checkAuth } } = useAppProvider()
  
  const [formData, setFormData] = useState({
    business_strategy: '',
    marketing_strategy: '',
    content_strategy: '',
    channel_strategy: '',
    growth_strategy: '',
    campaign_strategy: ''
  })

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [fetchError, setFetchError] = useState<string | null>(null)

  useEffect(() => {
    async function loadStrategy() {
      if (!activeBrand?.id) return
      setLoading(true)
      try {
        const res = (await ApiClient.get('/api/brand-brain/strategy')) as any
        setFormData({
          business_strategy: res.business_strategy || '',
          marketing_strategy: res.marketing_strategy || '',
          content_strategy: res.content_strategy || '',
          channel_strategy: res.channel_strategy || '',
          growth_strategy: res.growth_strategy || '',
          campaign_strategy: res.campaign_strategy || ''
        })
      } catch (err: any) {
        if (err.status !== 404) {
          setFetchError("Failed to load strategy")
        }
      } finally {
        setLoading(false)
      }
    }
    loadStrategy()
  }, [activeBrand])

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }))
    setSuccess(false)
    setError(null)
  }

  const handleSave = async () => {
    if (!activeBrand?.id) return
    setSaving(true)
    setError(null)
    setSuccess(false)

    try {
      await ApiClient.patch('/api/brand-brain/strategy', formData)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err: any) {
      setError(err.message || 'Failed to update strategy')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-[#A9A4A0] animate-spin" />
      </div>
    )
  }
  
  // Helpers for states
  const isGenerating = false // We could poll for this if we knew the task id, but for now we look at the states
  const isNotConfigured = formData.business_strategy === 'NOT_CONFIGURED'
  const isPartial = formData.business_strategy === 'PARTIAL'
  const isFailed = formData.business_strategy === 'FAILED'
  const isNoStrategy = !formData.business_strategy || isNotConfigured || isPartial || isFailed

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-6 bg-[#1C1A1A]">
      <div className="max-w-3xl space-y-8 pb-10">
        
        {/* Header */}
        <div>
          <h2 className="text-[18px] font-bold text-[#F5F3F1] flex items-center gap-2">
            <FileText className="w-5 h-5 text-[#8F0028]" />
            Core Strategy
          </h2>
          <p className="text-[13px] text-[#A9A4A0] mt-1">
            The synthesized strategic direction that all AI CMO agents will use to coordinate activities.
          </p>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg flex items-center gap-2 text-red-500 text-[13px]">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {fetchError && (
          <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg flex items-center gap-2 text-red-500 text-[13px]">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {fetchError}
          </div>
        )}

        {isNotConfigured && (
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/50 rounded-lg text-yellow-500 text-[13px]">
            Strategy generation is not configured. (Missing AI Gateway config)
          </div>
        )}

        {isPartial && (
          <div className="p-3 bg-blue-500/10 border border-blue-500/50 rounded-lg text-blue-500 text-[13px]">
            Strategy generation is incomplete due to insufficient website research. Please upload more documents.
          </div>
        )}

        {isFailed && (
          <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-500 text-[13px]">
            Strategy generation failed. Please try again or edit manually.
          </div>
        )}
        
        {(!formData.business_strategy) && (
          <div className="p-3 bg-[#242222] border border-[#373333] rounded-lg text-[#A9A4A0] text-[13px]">
            No strategy available yet.
          </div>
        )}

        <div className="space-y-6">
          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Business Strategy</label>
            <textarea 
              name="business_strategy"
              value={isNoStrategy ? '' : formData.business_strategy}
              onChange={handleChange}
              placeholder="Core business strategy..."
              rows={4}
              className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors custom-scrollbar resize-y"
            />
          </div>

          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Marketing Strategy</label>
            <textarea 
              name="marketing_strategy"
              value={formData.marketing_strategy}
              onChange={handleChange}
              placeholder="Overall marketing strategy..."
              rows={4}
              className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors custom-scrollbar resize-y"
            />
          </div>

          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Content Strategy</label>
            <textarea 
              name="content_strategy"
              value={formData.content_strategy}
              onChange={handleChange}
              placeholder="Content generation strategy..."
              rows={4}
              className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors custom-scrollbar resize-y"
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Channel Strategy</label>
            <textarea 
              name="channel_strategy"
              value={formData.channel_strategy}
              onChange={handleChange}
              placeholder="Where should content be published..."
              rows={4}
              className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors custom-scrollbar resize-y"
            />
          </div>

          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Growth Strategy</label>
            <textarea 
              name="growth_strategy"
              value={formData.growth_strategy}
              onChange={handleChange}
              placeholder="Tactics for scaling..."
              rows={4}
              className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors custom-scrollbar resize-y"
            />
          </div>

          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Campaign Strategy</label>
            <textarea 
              name="campaign_strategy"
              value={formData.campaign_strategy}
              onChange={handleChange}
              placeholder="Short-to-mid term campaign ideas..."
              rows={4}
              className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors custom-scrollbar resize-y"
            />
          </div>
        </div>

        {/* Footer Actions */}
        <div className="pt-6 border-t border-[#373333] flex items-center justify-between sticky bottom-0 bg-[#1C1A1A] z-10 py-4">
          <div>
            {success && <span className="text-[#00A650] text-[13px] font-bold">✓ Saved successfully</span>}
          </div>
          <button 
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 bg-[#8F0028] hover:bg-[#A3002D] disabled:opacity-50 text-white text-[13px] font-bold rounded-lg transition-colors flex items-center gap-2 shadow-lg shadow-[#8F0028]/20"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {saving ? 'Saving...' : 'Save Strategy'}
          </button>
        </div>

      </div>
    </div>
  )
}
