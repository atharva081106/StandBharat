"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
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
  const [valueProposition, setValueProposition] = useState("")
  const [brandVoice, setBrandVoice] = useState<string[]>(['Professional'])
  const [targetDemographic, setTargetDemographic] = useState("")
  const [customerPainPoints, setCustomerPainPoints] = useState("")
  const [primaryObjective, setPrimaryObjective] = useState("Increase Brand Awareness")
  const [targetRevenue, setTargetRevenue] = useState("")
  const [competitors, setCompetitors] = useState(["", "", ""])

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
        localStorage.setItem('onboardingData', JSON.stringify({
          businessName,
          website,
          description,
          valueProposition,
          brandVoice,
          targetDemographic,
          customerPainPoints,
          primaryObjective,
          targetRevenue,
          competitors: competitors.filter(c => c.trim() !== "")
        }))
        
        const isApi = process.env.NEXT_PUBLIC_DATA_MODE === 'api'
        if (isApi) {
          const { ApiClient } = await import('@/lib/api/client')
          // Create Workspace
          const ws = await ApiClient.post<any>('/api/workspaces/', { name: businessName })
          // Create Brand
          const br = await ApiClient.post<any>('/api/brands/', {
            name: businessName,
            workspace_id: ws.id,
            website_url: website,
            description: description
          }, { headers: { 'X-Workspace-ID': ws.id } })
          await checkAuth() // To fetch workspace info

          // Submit the rest of the onboarding data to configure the brand
          await ApiClient.post('/api/onboarding/complete', {
            businessName,
            website,
            description,
            valueProposition,
            brandVoice,
            targetDemographic,
            customerPainPoints,
            primaryObjective,
            targetRevenue,
            competitors: competitors.filter(c => c.trim() !== "")
          }, { headers: { 'X-Workspace-ID': ws.id, 'X-Brand-ID': br.id } })
        }
        setAuthState('onboardingComplete')
        router.push('/app')
      } catch (e) {
        alert("Failed to complete setup")
      }
      setLoading(false)
    }
  }

  const handleBack = () => {
    if (stepIdx > 0) {
      setStepIdx(stepIdx - 1)
    } else {
      router.push('/landingpage')
    }
  }

  return (
    <div className="h-screen flex flex-col bg-[#FAF8F3] overflow-hidden">
      <header className="px-8 py-5 border-b border-[#E8E4DC] bg-white flex justify-between items-center sticky top-0 z-50">
        <div className="w-1/3 flex justify-start">
          <Button 
            variant="outline"
            onClick={handleBack} 
            disabled={loading}
            className="h-10 px-4 bg-white hover:bg-[#FAF8F3] text-[#111111] font-bold text-[13px] rounded-xl transition-all border border-[#E8E4DC] shadow-sm flex items-center gap-1.5"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" /></svg>
            Back
          </Button>
        </div>
        <div className="w-1/3 flex justify-center">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/logo.jpg" alt="StandBharat Logo" width={28} height={28} className="rounded-lg object-contain shadow-sm border border-black/5" />
            <span className="font-bold text-lg tracking-tight text-[#111111] hidden sm:block">StandBharat</span>
          </Link>
        </div>
        <div className="w-1/3 flex justify-end">
          <div className="text-[13px] font-bold flex items-center gap-4">
            <span className="text-[#800020] hidden md:block">Step {stepIdx + 1} of {steps.length}</span>
            <div className="flex items-center relative">
               <div className="absolute left-0 right-0 h-[1px] bg-[#E8E4DC] top-1/2 -translate-y-1/2 z-0" />
               <div className="flex items-center gap-3 relative z-10">
                 {steps.map((s, i) => (
                    <div key={s} className={`w-2.5 h-2.5 rounded-full ring-4 ring-white ${i === stepIdx ? 'bg-[#800020]' : i < stepIdx ? 'bg-[#800020]/50' : 'bg-[#E8E4DC]'}`} />
                 ))}
               </div>
            </div>
            <span className="text-[#5A5A5A] min-w-[70px] hidden sm:block text-right">{steps[stepIdx]}</span>
          </div>
        </div>
      </header>
      
      <div className="h-1 bg-[#E8E4DC] w-full absolute top-[76px] z-40">
        <div 
          className="h-full bg-[#800020] transition-all duration-500 ease-out" 
          style={{ width: `${((stepIdx + 1) / steps.length) * 100}%` }}
        />
      </div>
      
      <main className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8 overflow-hidden">
        <div className="max-w-5xl w-full h-full max-h-[650px] bg-white rounded-[24px] shadow-lg border border-[#E8E4DC] flex flex-col md:flex-row overflow-hidden">
          
          {/* Left Side: Dynamic Visual Container */}
          <div className="hidden md:flex w-2/5 bg-[#FDF8F6] border-r border-[#E8E4DC] p-10 flex-col relative overflow-hidden justify-between">
            <div className="relative z-10">
              <div className="w-10 h-10 bg-white rounded-xl border border-[#E8E4DC] flex items-center justify-center shadow-sm mb-6 text-[#800020]">
                {stepIdx === 0 && <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
                {stepIdx === 1 && <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>}
                {stepIdx === 2 && <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>}
                {stepIdx === 3 && <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>}
                {stepIdx === 4 && <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>}
                {stepIdx === 5 && <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>}
                {stepIdx === 6 && <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>}
              </div>
              <div className="text-[11px] font-bold text-[#858585] tracking-wider mb-2 uppercase">Step {stepIdx + 1} of {steps.length}</div>
              <h3 className="text-[28px] font-bold text-[#111111] tracking-tight mb-3">
                {stepIdx === 0 && "Business Profile"}
                {stepIdx === 1 && "Brand Voice"}
                {stepIdx === 2 && "Target Audience"}
                {stepIdx === 3 && "Marketing Goals"}
                {stepIdx === 4 && "Competitors"}
                {stepIdx === 5 && "AI Agent Assembly"}
                {stepIdx === 6 && "Ready to Launch"}
              </h3>
              <p className="text-[#5A5A5A] font-medium text-[15px] leading-relaxed pr-2">
                {stepIdx === 0 && "Your business details act as the foundation. Our AI uses this to tailor every strategy to your exact domain and industry."}
                {stepIdx === 1 && "Teach the AI how your brand speaks, so every message feels like you."}
                {stepIdx === 2 && "Define exactly who you want to reach. We'll identify where they spend their time and what messaging resonates with them."}
                {stepIdx === 3 && "Set your primary objectives. The AI will optimize all campaigns and content to drive towards these specific results."}
                {stepIdx === 4 && "Identify key players in your market. We'll analyze their strategies to find gaps and opportunities for your brand to stand out."}
                {stepIdx === 5 && "We are provisioning dedicated virtual agents that will execute your marketing loops autonomously."}
                {stepIdx === 6 && "Your autonomous marketing engine is primed. Access the dashboard to watch it work."}
              </p>
              
              {stepIdx === 1 && (
                <div className="mt-8 space-y-6">
                </div>
              )}
            </div>

            {/* Bottom Graphic (Floating Pills) */}
            {stepIdx === 0 && (
              <div className="absolute -bottom-12 -right-8 w-[130%] h-[280px] flex items-center justify-center pointer-events-none">
                 <div className="absolute w-[400px] h-[400px] bg-[#800020]/5 rounded-full blur-3xl mix-blend-multiply" />
                 <div className="absolute w-[200px] h-[200px] bg-[#800020]/10 rounded-full blur-2xl mix-blend-multiply" />
                 
                 <div className="relative z-10 transform -rotate-[15deg] w-[220px] bg-white/90 backdrop-blur-md rounded-2xl shadow-xl border border-white p-5 mt-10">
                    <div className="flex items-center gap-2 mb-4">
                       <div className="w-6 h-6 rounded-md bg-[#800020] flex items-center justify-center"><div className="w-2 h-2 rounded-full bg-white"/></div>
                       <span className="font-bold text-[14px]">StandBharat</span>
                    </div>
                    <div className="space-y-3">
                       <div className="h-2 w-3/4 bg-[#E8E4DC] rounded-full" />
                       <div className="h-2 w-1/2 bg-[#E8E4DC] rounded-full" />
                       <div className="h-2 w-full bg-[#E8E4DC] rounded-full" />
                    </div>
                    <div className="mt-5 flex items-end gap-2 justify-end">
                       <div className="w-3 h-5 bg-[#E8E4DC] rounded-t-sm" />
                       <div className="w-3 h-8 bg-[#800020]/40 rounded-t-sm" />
                       <div className="w-3 h-12 bg-[#800020]/60 rounded-t-sm" />
                    </div>
                 </div>

                 {/* Floating Pills */}
                 <div className="absolute top-[15%] left-[10%] px-3.5 py-1.5 bg-white shadow-md border border-[#E8E4DC]/50 rounded-full text-[10px] font-bold text-[#800020] -rotate-12">Your Business</div>
                 <div className="absolute bottom-[20%] left-[8%] px-3.5 py-1.5 bg-white shadow-md border border-[#E8E4DC]/50 rounded-full text-[10px] font-bold text-[#800020] rotate-12">Your Customers</div>
                 <div className="absolute top-[45%] right-[10%] px-3.5 py-1.5 bg-white shadow-md border border-[#E8E4DC]/50 rounded-full text-[10px] font-bold text-[#800020] rotate-[10deg]">Your Market</div>
              </div>
            )}

            {/* Step 2 Bottom Graphic */}
            {stepIdx === 1 && (
              <div className="absolute -bottom-12 -right-8 w-[130%] h-[280px] flex items-center justify-center pointer-events-none">
                 <div className="absolute w-[400px] h-[400px] bg-[#800020]/5 rounded-full blur-3xl mix-blend-multiply" />
                 <div className="absolute w-[200px] h-[200px] bg-[#800020]/10 rounded-full blur-2xl mix-blend-multiply" />
                 
                 <div className="relative z-10 transform rotate-[10deg] w-[220px] bg-white/90 backdrop-blur-md rounded-2xl shadow-xl border border-white p-5 mt-10">
                    <div className="flex items-center gap-2 mb-4">
                       <div className="w-6 h-6 rounded-md bg-[#800020] flex items-center justify-center"><div className="w-2 h-2 rounded-full bg-white"/></div>
                       <span className="font-bold text-[14px]">StandBharat</span>
                    </div>
                    <div className="space-y-3">
                       <div className="h-2 w-3/4 bg-[#E8E4DC] rounded-full" />
                       <div className="h-2 w-1/2 bg-[#E8E4DC] rounded-full" />
                    </div>
                    <div className="mt-4 pt-4 border-t border-[#E8E4DC]">
                       <div className="text-[9px] font-bold text-[#858585] mb-2 uppercase tracking-wider">Brand Voice</div>
                       <div className="flex flex-wrap gap-1.5">
                          <div className="px-2 py-1 bg-[#FAF8F3] rounded text-[9px] text-[#5A5A5A] font-medium border border-[#E8E4DC]">Professional</div>
                          <div className="px-2 py-1 bg-[#FAF8F3] rounded text-[9px] text-[#5A5A5A] font-medium border border-[#E8E4DC]">Friendly</div>
                          <div className="px-2 py-1 bg-[#FAF8F3] rounded text-[9px] text-[#5A5A5A] font-medium border border-[#E8E4DC]">Technical</div>
                          <div className="px-2 py-1 bg-[#FAF8F3] rounded text-[9px] text-[#5A5A5A] font-medium border border-[#E8E4DC]">Premium</div>
                       </div>
                    </div>
                 </div>

                 {/* Floating Pills */}
                 <div className="absolute top-[35%] left-[8%] px-3.5 py-1.5 bg-white shadow-md border border-[#E8E4DC]/50 rounded-full text-[10px] font-bold text-[#800020] flex items-center gap-1.5 -rotate-[10deg]">
                   <span className="w-1.5 h-1.5 rounded-full bg-[#800020]"></span>Tone
                 </div>
                 <div className="absolute bottom-[25%] right-[12%] px-3.5 py-1.5 bg-white shadow-md border border-[#E8E4DC]/50 rounded-full text-[10px] font-bold text-[#800020] flex items-center gap-1.5 rotate-[15deg]">
                   <span className="w-1.5 h-1.5 rounded-full bg-[#800020]/40"></span>Style
                 </div>
              </div>
            )}
            
            {stepIdx > 1 && stepIdx < 5 && (
              <div className="absolute -bottom-24 -left-24 w-80 h-80 bg-[#800020]/5 rounded-full blur-3xl"></div>
            )}
            
            {(stepIdx === 2 || stepIdx === 3 || stepIdx === 4) && (
              <div className="absolute top-[25%] -right-12 w-64 h-64 bg-[#111111]/5 rounded-full blur-3xl pointer-events-none"></div>
            )}
            
            {stepIdx === 2 && (
              <div className="absolute -bottom-8 -right-8 w-full h-[250px] flex items-center justify-center pointer-events-none">
                 <div className="relative w-48 h-48 rounded-full border border-[#E8E4DC] flex items-center justify-center">
                   <div className="absolute w-full h-full animate-[spin_30s_linear_infinite]">
                     <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full border border-[#E8E4DC] shadow-sm flex items-center justify-center">
                       <div className="w-2 h-2 bg-[#800020] rounded-full"></div>
                     </div>
                     <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-6 h-6 bg-white rounded-full border border-[#E8E4DC] shadow-sm flex items-center justify-center">
                       <div className="w-1.5 h-1.5 bg-[#5A5A5A] rounded-full"></div>
                     </div>
                   </div>
                   <div className="w-32 h-32 rounded-full border border-[#E8E4DC]/50 flex items-center justify-center">
                     <div className="w-16 h-16 bg-[#800020]/10 rounded-full flex items-center justify-center animate-pulse">
                       <svg className="w-6 h-6 text-[#800020]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                     </div>
                   </div>
                 </div>
              </div>
            )}

            {stepIdx === 3 && (
              <div className="absolute -bottom-8 -right-8 w-full h-[250px] flex items-center justify-center pointer-events-none">
                 <div className="relative w-48 h-48">
                    {/* Minimal Bar Chart Graphic */}
                    <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex items-end gap-3 h-32 w-40 bg-white/50 backdrop-blur-sm p-4 rounded-xl border border-[#E8E4DC] shadow-sm">
                       <div className="w-full bg-[#E8E4DC] rounded-t-sm h-[30%]"></div>
                       <div className="w-full bg-[#E8E4DC] rounded-t-sm h-[50%]"></div>
                       <div className="w-full bg-[#800020]/60 rounded-t-sm h-[70%]"></div>
                       <div className="w-full bg-[#800020] rounded-t-sm h-[100%] shadow-[0_0_15px_rgba(128,0,32,0.3)]"></div>
                    </div>
                 </div>
              </div>
            )}

            {stepIdx === 4 && (
              <div className="absolute -bottom-8 -right-8 w-full h-[250px] flex items-center justify-center pointer-events-none">
                 <div className="relative w-56 h-56 flex items-center justify-center">
                    <div className="absolute top-10 left-4 w-16 h-16 bg-white rounded-xl shadow-md border border-[#E8E4DC] flex items-center justify-center rotate-[-10deg]">
                       <div className="w-8 h-2 bg-[#E8E4DC] rounded-full"></div>
                    </div>
                    <div className="absolute top-8 right-8 w-20 h-20 bg-white rounded-xl shadow-md border border-[#E8E4DC] flex items-center justify-center rotate-[15deg]">
                       <div className="w-10 h-2 bg-[#E8E4DC] rounded-full"></div>
                    </div>
                    <div className="relative z-10 w-24 h-24 bg-white rounded-xl shadow-xl border border-[#800020]/20 flex items-center justify-center flex-col gap-2">
                       <div className="w-6 h-6 rounded-md bg-[#800020] flex items-center justify-center"><div className="w-2 h-2 rounded-full bg-white"/></div>
                       <div className="w-12 h-2 bg-[#800020]/20 rounded-full"></div>
                    </div>
                 </div>
              </div>
            )}

            {stepIdx === 5 && (
              <div className="absolute -bottom-4 -right-4 w-full h-[280px] flex items-center justify-center pointer-events-none">
                 <div className="absolute w-[300px] h-[300px] bg-[#800020]/5 rounded-full blur-3xl mix-blend-multiply" />
                 <div className="relative w-48 h-48">
                    {/* Center Brain/Hub */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 bg-white rounded-2xl shadow-lg border border-[#800020]/20 flex items-center justify-center z-20">
                      <svg className="w-6 h-6 text-[#800020] animate-pulse" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>
                    </div>
                    {/* Orbiting Nodes */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full border border-dashed border-[#E8E4DC] rounded-full animate-[spin_20s_linear_infinite] z-10">
                      <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-lg border border-[#E8E4DC] shadow-sm flex items-center justify-center text-[10px] font-bold text-[#111111]">A</div>
                      <div className="absolute bottom-4 left-4 w-8 h-8 bg-white rounded-lg border border-[#E8E4DC] shadow-sm flex items-center justify-center text-[10px] font-bold text-[#111111] rotate-[120deg]">S</div>
                      <div className="absolute bottom-4 right-4 w-8 h-8 bg-white rounded-lg border border-[#E8E4DC] shadow-sm flex items-center justify-center text-[10px] font-bold text-[#111111] rotate-[240deg]">G</div>
                    </div>
                 </div>
              </div>
            )}

            {stepIdx === 6 && (
              <div className="absolute -bottom-8 -right-8 w-full h-[300px] flex items-center justify-center pointer-events-none">
                 <div className="absolute w-[400px] h-[400px] bg-[#008A2E]/5 rounded-full blur-3xl mix-blend-multiply" />
                 <div className="relative w-32 h-32 bg-white rounded-full shadow-xl border border-[#008A2E]/20 flex items-center justify-center animate-in zoom-in duration-700">
                    <svg className="w-12 h-12 text-[#008A2E]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                 </div>
              </div>
            )}
          </div>

          {/* Right Side: Interactive Form */}
          <div className="w-full md:w-3/5 px-8 pb-8 pt-4 sm:px-10 sm:pb-10 sm:pt-6 lg:px-12 lg:pb-12 lg:pt-8 flex flex-col h-full bg-white relative overflow-hidden">
            <div className="flex-1 flex flex-col justify-start max-w-md mx-auto w-full">
              
              {stepIdx === 0 && (
                <div className="animate-in fade-in duration-500 slide-in-from-right-4">
                  <div className="text-[11px] font-bold text-[#858585] tracking-wider mb-2 uppercase">Let's Get Started</div>
                  <h2 className="text-[32px] font-bold text-[#111111] mb-2 tracking-tight">Tell us about your business</h2>
                  <p className="text-[#5A5A5A] font-medium text-[15px] mb-8">We'll use this information to build your AI marketing engine.</p>
                  
                  <div className="space-y-6">
                    <div>
                      <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wider">Business name <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#858585]">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
                        </div>
                        <Input 
                          placeholder="Acme Corp" 
                          value={businessName} 
                          onChange={e => setBusinessName(e.target.value)} 
                          required 
                          className="h-11 pl-10 bg-white border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-xl shadow-sm"
                        />
                      </div>
                      <p className="text-[11px] text-[#858585] mt-1.5">Enter your official business or brand name.</p>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wider">Website URL</label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#858585]">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
                        </div>
                        <Input 
                          placeholder="https://acme.com" 
                          value={website} 
                          onChange={e => setWebsite(e.target.value)} 
                          className="h-11 pl-10 bg-white border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-xl shadow-sm"
                        />
                      </div>
                      <p className="text-[11px] text-[#858585] mt-1.5">Your website helps us understand your business, industry and positioning.</p>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wider">Business description <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <div className="absolute top-3 left-3 text-[#858585] pointer-events-none">
                           <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                        </div>
                        <textarea 
                          className="w-full rounded-xl bg-white border border-[#E8E4DC] pl-10 pr-3 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#800020] placeholder:text-[#858585] transition-all resize-none shadow-sm" 
                          rows={3}
                          placeholder="What does your business do? Who are your customers?"
                          value={description}
                          maxLength={500}
                          onChange={e => setDescription(e.target.value)}
                        ></textarea>
                        <div className="absolute bottom-3 right-3 text-[10px] font-bold text-[#858585]">
                          {description.length}/500
                        </div>
                      </div>
                      <p className="text-[11px] text-[#858585] mt-1.5">Share a brief overview of your business, what you do, and who your customers are.</p>
                    </div>
                  </div>
                </div>
              )}

              {stepIdx === 1 && (
                <div className="animate-in fade-in duration-500 slide-in-from-right-4">
                  <div className="text-[11px] font-bold text-[#858585] tracking-wider mb-2 uppercase">Let's Define Your Brand</div>
                  <h2 className="text-[32px] font-bold text-[#111111] mb-2 tracking-tight">Build your Brand Brain</h2>
                  <p className="text-[#5A5A5A] font-medium text-[15px] mb-8">This helps agents write and act exactly like your brand.</p>
                  
                  <div className="space-y-6">
                    <div>
                      <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wider">Value proposition <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#800020]">
                          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
                        </div>
                        <Input 
                          placeholder="What makes you unique?" 
                          value={valueProposition}
                          onChange={e => setValueProposition(e.target.value)}
                          className="h-11 pl-10 bg-white border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-xl shadow-sm"
                        />
                      </div>
                      <p className="text-[11px] text-[#858585] mt-1.5">Your one-line reason customers choose you.</p>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-[#111111] mb-3 uppercase tracking-wider">Brand voice</label>
                      <div className="flex flex-wrap gap-2">
                        {["Professional", "Friendly", "Bold", "Technical", "Premium", "Playful", "Minimal", "Authoritative"].map(v => (
                          <label key={v} className="cursor-pointer">
                            <input 
                              type="checkbox" 
                              className="peer sr-only" 
                              checked={brandVoice.includes(v)} 
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setBrandVoice([...brandVoice, v])
                                } else {
                                  setBrandVoice(brandVoice.filter(x => x !== v))
                                }
                              }}
                            />
                            <div className="px-4 py-2 bg-white border border-[#E8E4DC] rounded-full text-xs font-medium text-[#111111] peer-checked:bg-[#800020]/10 peer-checked:text-[#800020] peer-checked:border-[#800020] hover:border-[#800020]/50 transition-colors shadow-sm">
                              {v}
                            </div>
                          </label>
                        ))}
                      </div>
                    </div>

                  </div>
                </div>
              )}
              {stepIdx === 2 && (
                <div className="animate-in fade-in duration-500 slide-in-from-right-4">
                  <div className="text-[11px] font-bold text-[#858585] tracking-wider mb-2 uppercase">Let's Define Your Audience</div>
                  <h2 className="text-[32px] font-bold text-[#111111] mb-2 tracking-tight">Target Audience</h2>
                  <p className="text-[#5A5A5A] font-medium text-[15px] mb-8">Identify who you want to reach and where they spend their time.</p>
                  
                  <div className="space-y-6">
                    <div>
                      <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wider">Target Demographic <span className="text-red-500">*</span></label>
                      <Input 
                        placeholder="e.g. B2B SaaS Founders, 25-45" 
                        value={targetDemographic}
                        onChange={e => setTargetDemographic(e.target.value)}
                        className="h-11 px-4 bg-white border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-xl shadow-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wider">Customer Pain Points</label>
                      <textarea 
                        className="w-full rounded-xl bg-white border border-[#E8E4DC] px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#800020] placeholder:text-[#858585] transition-all resize-none shadow-sm" 
                        rows={3}
                        value={customerPainPoints}
                        onChange={e => setCustomerPainPoints(e.target.value)}
                        placeholder="What problems are they trying to solve?"
                      ></textarea>
                    </div>
                  </div>
                </div>
              )}

              {stepIdx === 3 && (
                <div className="animate-in fade-in duration-500 slide-in-from-right-4">
                  <div className="text-[11px] font-bold text-[#858585] tracking-wider mb-2 uppercase">Let's Define Your Goals</div>
                  <h2 className="text-[32px] font-bold text-[#111111] mb-2 tracking-tight">Marketing Goals</h2>
                  <p className="text-[#5A5A5A] font-medium text-[15px] mb-8">Set the objectives for your AI marketing engine.</p>
                  
                  <div className="space-y-6">
                    <div>
                      <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wider">Primary Objective <span className="text-red-500">*</span></label>
                      <div className="relative">
                        <select 
                          value={primaryObjective}
                          onChange={e => setPrimaryObjective(e.target.value)}
                          className="w-full h-11 px-4 bg-white border border-[#E8E4DC] focus:outline-none focus:ring-2 focus:ring-[#800020] text-sm font-medium rounded-xl shadow-sm appearance-none"
                        >
                           <option>Increase Brand Awareness</option>
                           <option>Generate Qualified Leads</option>
                           <option>Boost Sales/Revenue</option>
                           <option>Improve Customer Retention</option>
                        </select>
                        <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-[#5A5A5A]">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                        </div>
                      </div>
                    </div>
                    <div>
                      <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wider">Target Monthly Revenue</label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-[#111111] font-bold">$</div>
                        <Input 
                          placeholder="10,000" 
                          value={targetRevenue}
                          onChange={e => setTargetRevenue(e.target.value)}
                          className="h-11 pl-8 bg-white border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-xl shadow-sm"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {stepIdx === 4 && (
                <div className="animate-in fade-in duration-500 slide-in-from-right-4">
                  <div className="text-[11px] font-bold text-[#858585] tracking-wider mb-2 uppercase">Let's Identify Competitors</div>
                  <h2 className="text-[32px] font-bold text-[#111111] mb-2 tracking-tight">Competitors</h2>
                  <p className="text-[#5A5A5A] font-medium text-[15px] mb-8">Tell us who you're up against so we can find gaps in their strategy.</p>
                  
                  <div className="space-y-4">
                    {[1, 2, 3].map((num, idx) => (
                      <div key={num}>
                        <label className="block text-[11px] font-bold text-[#111111] mb-1.5 uppercase tracking-wider">Competitor {num} {num === 1 && <span className="text-red-500">*</span>}</label>
                        <Input 
                          placeholder={`Competitor ${num} URL or Name`} 
                          value={competitors[idx]}
                          onChange={e => {
                            const newComps = [...competitors];
                            newComps[idx] = e.target.value;
                            setCompetitors(newComps);
                          }}
                          className="h-11 px-4 bg-white border-[#E8E4DC] focus-visible:ring-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-xl shadow-sm"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {stepIdx === 5 && (
                <div className="animate-in fade-in duration-500 slide-in-from-right-4">
                  <div className="text-[11px] font-bold text-[#858585] tracking-wider mb-2 uppercase">System Provisioning</div>
                  <h2 className="text-[32px] font-bold text-[#111111] mb-2 tracking-tight">Assembling your AI Team</h2>
                  <p className="text-[#5A5A5A] font-medium text-[15px] mb-8">Provisioning specialized agents for your workspace.</p>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {[
                      { name: "Analytics Agent", color: "#F5E6E8" },
                      { name: "SEO Agent", color: "#F5E6E8" },
                      { name: "GEO Agent", color: "#F5E6E8" },
                      { name: "Writer Agent", color: "#F5E6E8" },
                      { name: "Growth Agent", color: "#F5E6E8" }
                    ].map((agent, i) => (
                      <div key={agent.name} className="p-3 bg-white border border-[#E8E4DC] rounded-xl flex items-center justify-between shadow-sm animate-in fade-in slide-in-from-bottom-2" style={{ animationDelay: `${i * 100}ms`, animationFillMode: 'both' }}>
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-[#F5E6E8] flex items-center justify-center text-[#800020] font-bold text-xs">
                            {agent.name.charAt(0)}
                          </div>
                          <span className="font-bold text-[#111111] text-[13px]">{agent.name}</span>
                        </div>
                        <span className="flex items-center gap-1 text-[#008A2E] text-[10px] font-bold uppercase tracking-wider">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#008A2E] animate-pulse" />
                          Ready
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {stepIdx === 6 && (
                <div className="animate-in fade-in duration-500 text-center py-6 slide-in-from-bottom-4 flex flex-col items-center justify-center h-full">
                  <div className="text-[11px] font-bold text-[#858585] tracking-wider mb-6 uppercase">System Ready</div>
                  <div className="w-24 h-24 bg-[#800020] rounded-[28px] flex items-center justify-center mx-auto mb-8 shadow-2xl shadow-[#800020]/30 rotate-3">
                    <svg className="w-12 h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h2 className="text-[32px] font-bold text-[#111111] tracking-tight mb-3">Your AI system is ready</h2>
                  <p className="text-[15px] text-[#5A5A5A] font-medium max-w-sm mx-auto mb-2">
                    Brand, Audience, Goals, Competitors, and AI team have been successfully configured.
                  </p>
                </div>
              )}
            </div>

          </div>
        </div>
      </main>

      {/* Global Continue Button */}
      <Button 
        onClick={handleNext} 
        disabled={loading}
        className="fixed bottom-8 right-8 h-12 px-8 bg-[#800020] hover:bg-[#5C0017] text-white font-bold text-sm rounded-xl transition-all duration-300 border-none shadow-xl shadow-[#800020]/30 hover:shadow-2xl hover:shadow-[#800020]/40 flex items-center gap-2 z-50 hover:-translate-y-1"
      >
        {loading ? "Processing..." : (
          <>
             {stepIdx === steps.length - 1 ? 'Enter Dashboard' : 'Continue'}
             <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7 7"/></svg>
          </>
        )}
      </Button>
    </div>
  )
}
