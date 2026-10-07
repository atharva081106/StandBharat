"use client"
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/lib/providers/MockProvider'

export default function Onboarding() {
  const router = useRouter()
  const { setAuthState, checkAuth } = useAuth()
  
  const [businessName, setBusinessName] = useState("")
  const [website, setWebsite] = useState("")
  const [description, setDescription] = useState("")
  const [audience, setAudience] = useState("")
  const [goal, setGoal] = useState("")
  const [loading, setLoading] = useState(false)
  const [selectedVoices, setSelectedVoices] = useState<string[]>([])
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const toggleVoice = (v: string) => {
    if (selectedVoices.includes(v)) {
      setSelectedVoices(selectedVoices.filter(voice => voice !== v))
    } else {
      setSelectedVoices([...selectedVoices, v])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!businessName) {
       alert("Business name is required")
       return
    }
    
    setLoading(true)
    try {
      const isApi = process.env.NEXT_PUBLIC_DATA_MODE === 'api'
      if (isApi) {
        const { ApiClient } = await import('@/lib/api/client')
        const ws = await ApiClient.post<any>('/api/workspaces/', { name: businessName })
        await ApiClient.post('/api/brands/', {
          name: businessName,
          workspace_id: ws.id,
          website_url: website,
          description: description
        }, { headers: { 'X-Workspace-ID': ws.id } })
        await checkAuth()
      }
      setAuthState('onboardingComplete')
      router.push('/app/command-center')
    } catch (e) {
      alert("Failed to complete setup")
    }
    setLoading(false)
  }

  return (
    <div className="h-screen w-full flex overflow-hidden bg-white">
      
      {/* LEFT COLUMN - FORM */}
      <div className="w-full lg:w-[55%] flex flex-col h-full border-r border-[#E8E4DC] relative z-10 bg-white">
        <header className="px-8 py-5 border-b border-[#E8E4DC] bg-white flex justify-between items-center shrink-0">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-[#800020] flex items-center justify-center shadow-sm">
              <div className="w-2 h-2 rounded-full bg-white" />
            </div>
            <span className="font-bold text-lg tracking-tight text-[#111111]">StandBharat</span>
          </Link>
          <div className="text-xs font-bold text-[#800020] bg-[#F5E6E8] px-3 py-1 rounded-full uppercase tracking-wider">
            Workspace Setup
          </div>
        </header>
        
        <main className="flex-1 flex flex-col p-8 lg:p-12 overflow-y-auto">
          <div className="max-w-xl w-full mx-auto flex flex-col h-full">
            
            <div className="mb-6 shrink-0">
              <h2 className="text-3xl font-bold text-[#111111] tracking-tight mb-2">Initialize your Brand Brain</h2>
              <p className="text-[#5A5A5A] text-sm font-medium">Provide a baseline so your AI CMO can generate highly targeted strategies, content, and campaigns instantly.</p>
            </div>

            <form id="onboarding-form" onSubmit={handleSubmit} className="space-y-6 flex-1">
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wide">Business Name *</label>
                  <Input 
                    placeholder="Acme Corp" 
                    value={businessName} 
                    onChange={e => setBusinessName(e.target.value)} 
                    required 
                    className="h-11 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wide">Website URL</label>
                  <Input 
                    placeholder="https://acme.com" 
                    value={website} 
                    onChange={e => setWebsite(e.target.value)} 
                    className="h-11 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg shadow-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wide">Target Audience</label>
                  <Input 
                    placeholder="e.g. Enterprise B2B SaaS" 
                    value={audience} 
                    onChange={e => setAudience(e.target.value)} 
                    className="h-11 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wide">Primary Goal</label>
                  <Input 
                    placeholder="e.g. Increase inbound leads" 
                    value={goal} 
                    onChange={e => setGoal(e.target.value)} 
                    className="h-11 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg shadow-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wide">Business Description</label>
                <textarea 
                  className="w-full rounded-lg bg-[#FAF8F3] border border-[#E8E4DC] p-3.5 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#800020] placeholder:text-[#858585] transition-all resize-none shadow-sm" 
                  rows={2}
                  placeholder="What does your business do? What makes you unique?"
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                ></textarea>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-[#111111] mb-2.5 uppercase tracking-wide">Brand Voice Characteristics</label>
                <div className="flex flex-wrap gap-2.5">
                  {["Professional", "Friendly", "Bold", "Technical", "Premium", "Playful", "Minimalist"].map(v => (
                    <button
                      type="button"
                      key={v}
                      onClick={() => toggleVoice(v)}
                      className={`px-3.5 py-1.5 border rounded-full text-xs font-bold transition-all duration-200 ${
                        selectedVoices.includes(v) 
                          ? 'bg-[#800020] text-white border-[#800020] shadow-md shadow-[#800020]/20 translate-y-[-1px]' 
                          : 'bg-white border-[#E8E4DC] text-[#5A5A5A] hover:border-[#800020] hover:text-[#800020]'
                      }`}
                    >
                      {v}
                    </button>
                  ))}
                </div>
              </div>

            </form>

            <div className="pt-6 mt-auto border-t border-[#E8E4DC] shrink-0 flex items-center justify-between">
              <p className="text-xs text-[#858585] font-medium hidden sm:block">
                All parameters can be tuned later.
              </p>
              <Button 
                type="submit"
                form="onboarding-form"
                disabled={loading}
                className="h-12 px-8 bg-[#800020] hover:bg-[#5C0017] text-white font-bold text-sm rounded-xl transition-all duration-200 border-none shadow-sm shadow-[#800020]/20 w-full sm:w-auto"
              >
                {loading ? "Provisioning Agents..." : "Initialize AI Team"} &rarr;
              </Button>
            </div>
          </div>
        </main>
      </div>

      {/* RIGHT COLUMN - VISUAL ELEMENTS */}
      <div className="hidden lg:flex w-[45%] bg-[#0A0A0A] relative flex-col items-center justify-center overflow-hidden">
        
        {/* Animated Background Gradients */}
        <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-[#800020] opacity-20 rounded-full blur-[100px] mix-blend-screen animate-pulse duration-1000"></div>
        <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-[#5C0017] opacity-30 rounded-full blur-[120px] mix-blend-screen" style={{ animation: 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite' }}></div>
        
        {/* Abstract Grid Overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>

        <div className="relative z-10 w-full max-w-md px-8 flex flex-col gap-6">
          
          {/* Visual Title */}
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-white mb-2">Assembling your team</h3>
            <p className="text-[#A1A1A1] text-sm">Real-time agent provisioning</p>
          </div>

          {/* Animated Agent Cards */}
          <div className="space-y-4">
            {/* Agent 1 */}
            <div className={`transform transition-all duration-1000 ${mounted ? 'translate-x-0 opacity-100' : 'translate-x-8 opacity-0'} bg-white/5 border border-white/10 backdrop-blur-md p-4 rounded-2xl flex items-center gap-4`}>
              <div className="w-10 h-10 rounded-xl bg-[#800020]/20 border border-[#800020]/40 flex items-center justify-center text-[#F5E6E8]">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="text-white text-sm font-bold">Growth Agent</h4>
                  <span className="text-[10px] font-bold text-[#A1A1A1] uppercase tracking-wider">Warming Up</span>
                </div>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-[#800020] to-[#E53E3E] w-[75%] rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>

            {/* Agent 2 */}
            <div className={`transform transition-all duration-1000 delay-200 ${mounted ? 'translate-x-0 opacity-100' : '-translate-x-8 opacity-0'} bg-white/5 border border-white/10 backdrop-blur-md p-4 rounded-2xl flex items-center gap-4 ml-6`}>
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="text-white text-sm font-bold">Content Agent</h4>
                  <span className="text-[10px] font-bold text-[#A1A1A1] uppercase tracking-wider">Initializing</span>
                </div>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-blue-600 to-blue-400 w-[45%] rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>

            {/* Agent 3 */}
            <div className={`transform transition-all duration-1000 delay-400 ${mounted ? 'translate-x-0 opacity-100' : 'translate-x-8 opacity-0'} bg-white/5 border border-white/10 backdrop-blur-md p-4 rounded-2xl flex items-center gap-4`}>
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="text-white text-sm font-bold">Analytics Agent</h4>
                  <span className="text-[10px] font-bold text-[#A1A1A1] uppercase tracking-wider">Connecting</span>
                </div>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-purple-600 to-purple-400 w-[15%] rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Dynamic feedback based on form input */}
          <div className={`mt-4 transform transition-all duration-700 ${businessName ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}>
            <div className="bg-[#800020]/20 border border-[#800020]/30 rounded-xl p-4 flex items-start gap-3">
              <svg className="w-5 h-5 text-[#F5E6E8] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <p className="text-sm text-[#F5E6E8] font-medium leading-relaxed">
                Brand Brain established for <span className="font-bold text-white">"{businessName}"</span>. Neural pathways linking brand guidelines to execution modules.
              </p>
            </div>
          </div>

        </div>
      </div>

    </div>
  )
}
