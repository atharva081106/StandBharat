"use client"
import { useState, useEffect } from 'react'
import { useAppProvider } from '@/lib/providers'
import { ApiClient } from '@/lib/api/client'
import { Briefcase, Save, Loader2, AlertCircle } from 'lucide-react'

export function BusinessOverviewPanel() {
  const { auth: { activeBrand, checkAuth } } = useAppProvider()
  
  const [formData, setFormData] = useState({
    name: '',
    website_url: '',
    industry: '',
    category: '',
    location: '',
    mission: '',
    vision: '',
    values: '',
    tagline: ''
  })

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  // Initialize with activeBrand data (from auth context) when loaded
  useEffect(() => {
    if (activeBrand) {
      // eslint-disable-next-line react-hooks/exhaustive-deps, react-hooks/set-state-in-effect
      setFormData({
        name: activeBrand.name || '',
        website_url: activeBrand.website_url || '',
        industry: activeBrand.industry || '',
        category: activeBrand.category || '',
        location: activeBrand.location || '',
        mission: activeBrand.mission || '',
        vision: activeBrand.vision || '',
        values: activeBrand.values || '',
        tagline: activeBrand.tagline || ''
      })
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLoading(false)
    } else {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLoading(true)
    }
  }, [activeBrand])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
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
      // We send the PATCH request to the API
      await ApiClient.patch(`/api/brands/${activeBrand.id}`, formData)
      
      // Refresh global context so TopBar and other areas update
      await checkAuth()
      
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err: any) {
      setError(err.message || 'Failed to update business overview')
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

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-6 bg-[#1C1A1A]">
      <div className="max-w-3xl space-y-8 pb-10">
        
        {/* Header */}
        <div>
          <h2 className="text-[18px] font-bold text-[#F5F3F1] flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-[#8F0028]" />
            Business Overview
          </h2>
          <p className="text-[13px] text-[#A9A4A0] mt-1">
            Define your core business identity. This context is used by the AI CMO and all specialized agents.
          </p>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg flex items-center gap-2 text-red-500 text-[13px]">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Business Name</label>
              <input 
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="e.g. Acme Corp"
                className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors"
              />
            </div>
            <div className="space-y-2">
              <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Website URL</label>
              <input 
                name="website_url"
                value={formData.website_url}
                onChange={handleChange}
                placeholder="e.g. https://acme.com"
                className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Industry</label>
              <input 
                name="industry"
                value={formData.industry}
                onChange={handleChange}
                placeholder="e.g. SaaS"
                className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors"
              />
            </div>
            <div className="space-y-2">
              <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Category</label>
              <input 
                name="category"
                value={formData.category}
                onChange={handleChange}
                placeholder="e.g. B2B Software"
                className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Location</label>
            <input 
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="e.g. Global / New York / Remote"
              className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors"
            />
          </div>

          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Tagline</label>
            <input 
              name="tagline"
              value={formData.tagline}
              onChange={handleChange}
              placeholder="Your short, catchy brand promise"
              className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors"
            />
          </div>

          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Mission</label>
            <textarea 
              name="mission"
              value={formData.mission}
              onChange={handleChange}
              placeholder="What is your company's core mission?"
              rows={3}
              className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors custom-scrollbar resize-y"
            />
          </div>

          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Vision</label>
            <textarea 
              name="vision"
              value={formData.vision}
              onChange={handleChange}
              placeholder="Where is your company heading in the long term?"
              rows={3}
              className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[13px] text-[#F5F3F1] focus:border-[#8F0028] outline-none transition-colors custom-scrollbar resize-y"
            />
          </div>

          <div className="space-y-2">
            <label className="text-[12px] font-bold text-[#A9A4A0] uppercase tracking-wider">Core Values</label>
            <textarea 
              name="values"
              value={formData.values}
              onChange={handleChange}
              placeholder="List the guiding principles of your brand"
              rows={3}
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
            {saving ? 'Saving...' : 'Save Overview'}
          </button>
        </div>

      </div>
    </div>
  )
}
