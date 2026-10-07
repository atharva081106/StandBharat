"use client"
import { useState } from 'react'
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
    <div className="h-screen flex flex-col bg-[#FAF8F3] overflow-hidden">
      <header className="px-6 py-4 border-b border-[#E8E4DC] bg-white flex justify-between items-center shrink-0">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-5 h-5 rounded flex items-center justify-center bg-[#800020]">
            <div className="w-1.5 h-1.5 rounded-full bg-white" />
          </div>
          <span className="font-bold text-base tracking-tight text-[#111111]">StandBharat</span>
        </Link>
        <div className="text-xs font-bold text-[#800020] bg-[#F5E6E8] px-3 py-1 rounded-full uppercase tracking-wider">
          Workspace Setup
        </div>
      </header>
      
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-3xl bg-white rounded-[20px] shadow-sm border border-[#E8E4DC] flex flex-col max-h-full">
          
          <div className="p-6 sm:p-8 pb-4 shrink-0 border-b border-[#E8E4DC]">
            <h2 className="text-2xl sm:text-3xl font-bold text-[#111111] tracking-tight mb-1">Set up your brand</h2>
            <p className="text-[#5A5A5A] text-sm font-medium">Configure your AI CMO parameters to instantly generate strategies and content.</p>
          </div>

          <div className="p-6 sm:p-8 overflow-y-auto">
            <form id="onboarding-form" onSubmit={handleSubmit} className="space-y-5">
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs font-bold text-[#111111] mb-1.5 uppercase tracking-wide">Business Name *</label>
                  <Input 
                    placeholder="Acme Corp" 
                    value={businessName} 
                    onChange={e => setBusinessName(e.target.value)} 
                    required 
                    className="h-10 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#111111] mb-1.5 uppercase tracking-wide">Website URL</label>
                  <Input 
                    placeholder="https://acme.com" 
                    value={website} 
                    onChange={e => setWebsite(e.target.value)} 
                    className="h-10 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs font-bold text-[#111111] mb-1.5 uppercase tracking-wide">Target Audience</label>
                  <Input 
                    placeholder="e.g. Enterprise B2B SaaS" 
                    value={audience} 
                    onChange={e => setAudience(e.target.value)} 
                    className="h-10 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#111111] mb-1.5 uppercase tracking-wide">Primary Goal</label>
                  <Input 
                    placeholder="e.g. Increase inbound leads" 
                    value={goal} 
                    onChange={e => setGoal(e.target.value)} 
                    className="h-10 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#111111] mb-1.5 uppercase tracking-wide">Business Description</label>
                <textarea 
                  className="w-full rounded-lg bg-[#FAF8F3] border border-[#E8E4DC] p-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#800020] placeholder:text-[#858585] transition-all resize-none" 
                  rows={2}
                  placeholder="What does your business do? What makes you unique?"
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                ></textarea>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#111111] mb-2 uppercase tracking-wide">Brand Voice</label>
                <div className="flex flex-wrap gap-2">
                  {["Professional", "Friendly", "Bold", "Technical", "Premium", "Playful"].map(v => (
                    <button
                      type="button"
                      key={v}
                      onClick={() => toggleVoice(v)}
                      className={`px-3 py-1.5 border rounded-full text-xs font-bold transition-colors ${
                        selectedVoices.includes(v) 
                          ? 'bg-[#800020] text-white border-[#800020]' 
                          : 'bg-white border-[#E8E4DC] text-[#5A5A5A] hover:border-[#800020] hover:text-[#800020]'
                      }`}
                    >
                      {v}
                    </button>
                  ))}
                </div>
              </div>

            </form>
          </div>

          <div className="p-6 sm:p-8 pt-4 border-t border-[#E8E4DC] shrink-0 flex items-center justify-between bg-white rounded-b-[20px]">
            <p className="text-xs text-[#858585] font-medium hidden sm:block">
              You can adjust these settings later in your Brand Brain.
            </p>
            <Button 
              type="submit"
              form="onboarding-form"
              disabled={loading}
              className="h-11 px-8 bg-[#800020] hover:bg-[#5C0017] text-white font-bold text-sm rounded-xl transition-all duration-200 border-none shadow-sm shadow-[#800020]/20 w-full sm:w-auto"
            >
              {loading ? "Provisioning Agents..." : "Initialize AI Team"} &rarr;
            </Button>
          </div>

        </div>
      </main>
    </div>
  )
}
