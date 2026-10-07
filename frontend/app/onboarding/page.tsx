"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/lib/providers/MockProvider'

const steps = ["Business", "Brand", "Audience", "Goals", "Competitors", "AI Setup", "Ready"]

export default function Onboarding() {
  const [stepIdx, setStepIdx] = useState(0)
  const router = useRouter()
  const { setAuthState, checkAuth } = useAuth()
  const [businessName, setBusinessName] = useState("")
  const [website, setWebsite] = useState("")
  const [description, setDescription] = useState("")
  const [loading, setLoading] = useState(false)

  const handleNext = async () => {
    if (stepIdx < steps.length - 1) {
      if (stepIdx === 0 && !businessName) {
         alert("Business name is required")
         return
      }
      setStepIdx(stepIdx + 1)
    } else {
      setLoading(true)
      try {
        const isApi = process.env.NEXT_PUBLIC_DATA_MODE === 'api'
        if (isApi) {
          const { ApiClient } = await import('@/lib/api/client')
          // Create Workspace
          const ws = await ApiClient.post<any>('/api/workspaces/', { name: businessName })
          // Create Brand
          await ApiClient.post('/api/brands/', {
            name: businessName,
            workspace_id: ws.id,
            website_url: website,
            description: description
          }, { headers: { 'X-Workspace-ID': ws.id } })
          await checkAuth() // To fetch workspace info
        }
        setAuthState('onboardingComplete')
        router.push('/app/command-center')
      } catch (e) {
        alert("Failed to complete setup")
      }
      setLoading(false)
    }
  }

  const handleBack = () => {
    if (stepIdx > 0) setStepIdx(stepIdx - 1)
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3]">
      <header className="px-8 py-5 border-b border-[#E8E4DC] bg-white flex justify-between items-center sticky top-0 z-50">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-[#800020] flex items-center justify-center">
            <div className="w-2 h-2 rounded-full bg-white" />
          </div>
          <span className="font-bold text-lg tracking-tight text-[#111111]">StandBharat</span>
        </Link>
        <div className="text-sm font-bold text-[#5A5A5A] flex items-center gap-2">
          <span className="text-[#800020]">Step {stepIdx + 1} of {steps.length}</span>
          <span className="text-[#E8E4DC]">&mdash;</span>
          <span>{steps[stepIdx]}</span>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="h-1 bg-[#E8E4DC] w-full">
        <div 
          className="h-full bg-[#800020] transition-all duration-500 ease-out" 
          style={{ width: `${((stepIdx + 1) / steps.length) * 100}%` }}
        />
      </div>
      
      <main className="flex-1 flex items-center justify-center p-6 sm:p-12">
        <div className="max-w-2xl w-full bg-white rounded-[24px] shadow-sm border border-[#E8E4DC] p-10 sm:p-14">
          
          {stepIdx === 0 && (
            <div className="animate-in fade-in duration-500 slide-in-from-bottom-4">
              <h2 className="text-3xl font-bold text-[#111111] mb-2 tracking-tight">Tell us about your business</h2>
              <p className="text-[#5A5A5A] font-medium mb-8">We'll use this to build your AI marketing engine.</p>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-bold text-[#111111] mb-2">Business name</label>
                  <Input 
                    placeholder="Acme Corp" 
                    value={businessName} 
                    onChange={e => setBusinessName(e.target.value)} 
                    required 
                    className="h-12 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-base font-medium placeholder:text-[#858585] rounded-xl"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-[#111111] mb-2">Website URL</label>
                  <Input 
                    placeholder="https://acme.com" 
                    value={website} 
                    onChange={e => setWebsite(e.target.value)} 
                    className="h-12 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-base font-medium placeholder:text-[#858585] rounded-xl"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-[#111111] mb-2">Business description</label>
                  <textarea 
                    className="w-full rounded-xl bg-[#FAF8F3] border border-[#E8E4DC] p-4 text-base font-medium focus:outline-none focus:ring-2 focus:ring-[#800020] placeholder:text-[#858585] transition-all resize-none" 
                    rows={4}
                    placeholder="What does your business do? Who are your customers?"
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                  ></textarea>
                </div>
              </div>
            </div>
          )}

          {stepIdx === 1 && (
            <div className="animate-in fade-in duration-500 slide-in-from-bottom-4">
              <h2 className="text-3xl font-bold text-[#111111] mb-2 tracking-tight">Build your Brand Brain</h2>
              <p className="text-[#5A5A5A] font-medium mb-8">This helps agents write and act exactly like your brand.</p>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-bold text-[#111111] mb-2">Value proposition</label>
                  <Input 
                    placeholder="What makes you unique?" 
                    className="h-12 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-base font-medium placeholder:text-[#858585] rounded-xl"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-[#111111] mb-3">Brand voice</label>
                  <div className="flex flex-wrap gap-2">
                    {["Professional", "Friendly", "Bold", "Technical", "Premium", "Playful", "Minimal", "Authoritative"].map(v => (
                      <label key={v} className="cursor-pointer">
                        <input type="checkbox" className="peer sr-only" />
                        <div className="px-4 py-2 bg-white border border-[#E8E4DC] rounded-full text-sm font-bold text-[#5A5A5A] peer-checked:bg-[#800020] peer-checked:text-white peer-checked:border-[#800020] hover:border-[#800020] transition-colors">
                          {v}
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {(stepIdx > 1 && stepIdx < 5) && (
            <div className="animate-in fade-in duration-500 slide-in-from-bottom-4">
              <h2 className="text-3xl font-bold text-[#111111] mb-2 tracking-tight">{steps[stepIdx]}</h2>
              <p className="text-[#5A5A5A] font-medium mb-8">Configuring your {steps[stepIdx].toLowerCase()} parameters...</p>
              <div>
                <Input 
                  placeholder={`Enter ${steps[stepIdx].toLowerCase()} info...`} 
                  className="h-12 bg-[#FAF8F3] border-[#E8E4DC] focus-visible:ring-[#800020] text-base font-medium placeholder:text-[#858585] rounded-xl"
                />
              </div>
            </div>
          )}
          
          {stepIdx === 5 && (
            <div className="animate-in fade-in duration-500 slide-in-from-bottom-4">
              <h2 className="text-3xl font-bold text-[#111111] mb-2 tracking-tight">Assembling your AI Team</h2>
              <p className="text-[#5A5A5A] font-medium mb-8">Provisioning specialized agents for your workspace.</p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { name: "Analytics Agent", color: "#F5E6E8" },
                  { name: "SEO Agent", color: "#F5E6E8" },
                  { name: "GEO Agent", color: "#F5E6E8" },
                  { name: "Writer Agent", color: "#F5E6E8" },
                  { name: "Growth Agent", color: "#F5E6E8" }
                ].map((agent, i) => (
                  <div key={agent.name} className="p-4 bg-white border border-[#E8E4DC] rounded-xl flex items-center justify-between shadow-sm animate-in fade-in slide-in-from-bottom-2" style={{ animationDelay: `${i * 100}ms`, animationFillMode: 'both' }}>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-[#F5E6E8] flex items-center justify-center text-[#800020] font-bold text-xs">
                        {agent.name.charAt(0)}
                      </div>
                      <span className="font-bold text-[#111111] text-sm">{agent.name}</span>
                    </div>
                    <span className="flex items-center gap-1.5 text-[#008A2E] text-xs font-bold uppercase tracking-wider">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#008A2E] animate-pulse" />
                      Ready
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {stepIdx === 6 && (
            <div className="animate-in fade-in duration-500 text-center py-10 slide-in-from-bottom-4">
              <div className="w-20 h-20 bg-[#800020] rounded-[24px] flex items-center justify-center mx-auto mb-8 shadow-xl shadow-[#800020]/20 rotate-3">
                <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-4xl font-bold text-[#111111] tracking-tight mb-4">Your AI system is ready</h2>
              <p className="text-lg text-[#5A5A5A] font-medium max-w-md mx-auto mb-2">
                Brand, Audience, Goals, Competitors, and AI team have been successfully configured.
              </p>
            </div>
          )}

          <div className="mt-12 flex justify-between border-t border-[#E8E4DC] pt-8">
            <Button 
              variant="outline" 
              onClick={handleBack} 
              disabled={stepIdx === 0}
              className={`h-12 px-6 rounded-xl font-bold text-base border-[#E8E4DC] transition-colors ${stepIdx === 0 ? 'opacity-0 pointer-events-none' : 'hover:bg-[#FAF8F3] text-[#111111]'}`}
            >
              Back
            </Button>
            <Button 
              onClick={handleNext} 
              disabled={loading}
              className="h-12 px-8 bg-[#800020] hover:bg-[#5C0017] text-white font-bold text-base rounded-xl transition-all duration-200 border-none shadow-sm shadow-[#800020]/20 ml-auto"
            >
              {loading ? "Processing..." : (stepIdx === steps.length - 1 ? 'Enter Command Center ?' : 'Continue')}
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
