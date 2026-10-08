"use client"
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { User, Zap, Building2, Check, Crown, AlignJustify, Brain, Target, BarChart2, TrendingUp } from 'lucide-react'


export function UseCasesSection() {
  return (
    <section className="py-32 px-6 lg:px-8 bg-white/60 backdrop-blur-sm border-y border-[#E8E4DC]">
      <div className="max-w-[1400px] mx-auto space-y-16">
        <div>
          <div className="text-center space-y-4">
            <h2 className="text-[40px] md:text-[48px] font-bold tracking-tight text-[#111111] leading-[1.1]">
              Built for every<br/>marketing leader.
            </h2>
            <p className="text-xl text-[#5A5A5A] font-medium max-w-2xl mx-auto">
              Whether you&apos;re a founder, marketing lead or growth team, StandBharat adapts to your goals.
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <div className="p-8 border border-[#E8E4DC] rounded-[24px] bg-[#FAF8F3]/80 hover:bg-white hover:shadow-xl hover:shadow-[#800020]/5 transition-all duration-300 h-full flex flex-col group relative overflow-hidden backdrop-blur-sm">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-[#800020]/10 to-transparent rounded-full blur-2xl -mr-10 -mt-10 transition-opacity group-hover:opacity-100 opacity-0" />
              <div className="h-14 mb-6 flex items-center">
                 <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="group-hover:scale-110 transition-transform duration-300">
                    <rect width="40" height="40" rx="8" fill="white" stroke="#E8E4DC" />
                    <path d="M12 28L20 16L28 22L36 8" stroke="#800020" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                    <circle cx="28" cy="22" r="3" fill="white" stroke="#800020" strokeWidth="2"/>
                 </svg>
              </div>
              <h3 className="text-xl font-bold text-[#111111] mb-3">Founders</h3>
              <p className="text-[#5A5A5A] font-medium leading-relaxed mt-auto">&quot;Know exactly what your marketing should do.&quot;</p>
            </div>
          </div>
          <div>
            <div className="p-8 border border-[#E8E4DC] rounded-[24px] bg-[#FAF8F3]/80 hover:bg-white hover:shadow-xl hover:shadow-blue-900/5 transition-all duration-300 h-full flex flex-col group relative overflow-hidden backdrop-blur-sm">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-blue-500/10 to-transparent rounded-full blur-2xl -mr-10 -mt-10 transition-opacity group-hover:opacity-100 opacity-0" />
              <div className="h-14 mb-6 flex items-center relative">
                 <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="group-hover:scale-110 transition-transform duration-300">
                    <rect width="40" height="40" rx="8" fill="white" stroke="#E8E4DC" />
                    <circle cx="20" cy="20" r="4" fill="#111111" />
                    <circle cx="12" cy="12" r="3" stroke="#111111" strokeWidth="2" />
                    <circle cx="28" cy="12" r="3" stroke="#111111" strokeWidth="2" />
                    <circle cx="12" cy="28" r="3" stroke="#111111" strokeWidth="2" />
                    <circle cx="28" cy="28" r="3" stroke="#111111" strokeWidth="2" />
                    <path d="M14 14L18 18M26 14L22 18M14 26L18 22M26 26L22 22" stroke="#111111" strokeWidth="1.5" strokeLinecap="round"/>
                 </svg>
              </div>
              <h3 className="text-xl font-bold text-[#111111] mb-3">Marketing Leads</h3>
              <p className="text-[#5A5A5A] font-medium leading-relaxed mt-auto">&quot;Turn strategy into coordinated execution.&quot;</p>
            </div>
          </div>
          <div>
            <div className="p-8 border border-[#E8E4DC] rounded-[24px] bg-[#FAF8F3]/80 hover:bg-white hover:shadow-xl hover:shadow-green-900/5 transition-all duration-300 h-full flex flex-col group relative overflow-hidden backdrop-blur-sm">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-green-500/10 to-transparent rounded-full blur-2xl -mr-10 -mt-10 transition-opacity group-hover:opacity-100 opacity-0" />
              <div className="h-14 mb-6 flex items-center relative">
                 <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="group-hover:scale-110 transition-transform duration-300">
                    <rect width="40" height="40" rx="8" fill="white" stroke="#E8E4DC" />
                    <rect x="12" y="14" width="16" height="20" rx="2" stroke="#168A5B" strokeWidth="2" fill="white" />
                    <rect x="16" y="10" width="16" height="20" rx="2" stroke="#168A5B" strokeWidth="2" strokeOpacity="0.4" fill="transparent" />
                    <line x1="16" y1="20" x2="24" y2="20" stroke="#168A5B" strokeWidth="2" strokeLinecap="round" />
                    <line x1="16" y1="24" x2="20" y2="24" stroke="#168A5B" strokeWidth="2" strokeLinecap="round" />
                 </svg>
              </div>
              <h3 className="text-xl font-bold text-[#111111] mb-3">Content Teams</h3>
              <p className="text-[#5A5A5A] font-medium leading-relaxed mt-auto">&quot;Create more without losing brand consistency.&quot;</p>
            </div>
          </div>
          <div>
            <div className="p-8 border border-[#E8E4DC] rounded-[24px] bg-[#FAF8F3]/80 hover:bg-white hover:shadow-xl hover:shadow-orange-900/5 transition-all duration-300 h-full flex flex-col group relative overflow-hidden backdrop-blur-sm">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-orange-500/10 to-transparent rounded-full blur-2xl -mr-10 -mt-10 transition-opacity group-hover:opacity-100 opacity-0" />
              <div className="h-14 mb-6 flex items-center">
                 <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="group-hover:scale-110 transition-transform duration-300">
                    <rect width="40" height="40" rx="8" fill="white" stroke="#E8E4DC" />
                    <path d="M12 12H28L22 22V28L18 30V22L12 12Z" stroke="#E67E22" strokeWidth="2" fill="transparent" strokeLinejoin="round"/>
                    <circle cx="20" cy="16" r="2" fill="#E67E22" />
                 </svg>
              </div>
              <h3 className="text-xl font-bold text-[#111111] mb-3">Growth Teams</h3>
              <p className="text-[#5A5A5A] font-medium leading-relaxed mt-auto">&quot;Find and act on high-value opportunities.&quot;</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export function PricingSection() {
  return (
    <section className="py-12 md:py-16 px-6 lg:px-8 relative overflow-hidden bg-gradient-to-br from-[#FFF5F6] via-[#FAF8F3] to-[#FFF0F2]" id="pricing">
      
      {/* Background Graphic Elements */}
      <div className="absolute inset-0 pointer-events-none opacity-40">
        <svg width="100%" height="100%" viewBox="0 0 1440 800" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
           <path d="M-100 400C200 100 600 -100 1000 200C1400 500 1600 400 1800 200" stroke="#800020" strokeWidth="0.5" strokeOpacity="0.3"/>
           <path d="M-100 600C300 300 700 300 1100 600C1500 900 1700 800 1900 600" stroke="#800020" strokeWidth="0.5" strokeOpacity="0.2"/>
        </svg>
      </div>
      
      {/* Floating Shapes */}
      <div className="absolute top-1/4 left-[15%] w-3 h-3 bg-[#E8A5B2] rotate-45 rounded-sm opacity-60"></div>
      <div className="absolute top-1/3 right-[15%] w-4 h-4 bg-[#800020] rotate-45 rounded-sm opacity-80"></div>
      <div className="absolute bottom-1/4 right-[5%] w-4 h-4 bg-[#D4939F] rotate-45 rounded-sm opacity-50"></div>
      
      <div className="absolute top-[35%] left-[5%] w-10 h-10 border border-[#E8A5B2] rounded-md rotate-12 opacity-30"></div>
      <div className="absolute top-[10%] right-[10%] w-16 h-16 border border-[#E8A5B2] rounded-full opacity-20 border-dashed"></div>

      {/* Side Typography - Left */}
      <div className="hidden xl:flex flex-col absolute left-8 top-1/3 space-y-2 z-10">
        <div className="w-4 h-[2px] bg-[#800020] mb-2"></div>
        <div className="text-[9px] font-bold tracking-[0.25em] text-[#858585]">STRATEGY</div>
        <div className="text-[9px] font-bold tracking-[0.25em] text-[#858585]">CONTENT</div>
        <div className="text-[9px] font-bold tracking-[0.25em] text-[#858585]">EXECUTION</div>
        <div className="text-[9px] font-bold tracking-[0.25em] text-[#858585]">PERFORMANCE</div>
      </div>

      {/* Side Typography - Right */}
      <div className="hidden xl:flex flex-col absolute right-8 bottom-1/4 space-y-2 z-10">
        <div className="w-4 h-[2px] bg-[#800020] mb-2"></div>
        <div className="text-[9px] font-bold tracking-[0.25em] text-[#858585]">BUILT FOR</div>
        <div className="text-[9px] font-bold tracking-[0.25em] text-[#858585]">MODERN</div>
        <div className="text-[9px] font-bold tracking-[0.25em] text-[#858585]">MARKETING</div>
        <div className="text-[9px] font-bold tracking-[0.25em] text-[#858585]">TEAMS</div>
      </div>

      <div className="max-w-[1100px] mx-auto text-center relative z-20">
        
        {/* Header */}
        <div className="flex flex-col items-center mb-10">
          <div className="inline-flex items-center gap-2 bg-[#F5E6E8] text-[#800020] px-4 py-1.5 rounded-full text-[10px] font-bold tracking-widest uppercase mb-5">
            <AlignJustify className="w-3 h-3" /> PRICING
          </div>
          <h2 className="text-[32px] md:text-[44px] font-extrabold tracking-tight text-[#111111] leading-[1.1] mb-3">
            Everything you need to run an <br className="hidden md:block" />
            <span className="text-[#800020]">autonomous marketing system.</span>
          </h2>
          <p className="text-sm md:text-base text-[#5A5A5A] font-medium max-w-2xl mx-auto mb-6">
            From strategy to execution — StandBharat gives you the AI CMO, specialized agents and integrations to grow your business, all in one platform.
          </p>
          
          {/* Toggle */}
          <div className="inline-flex items-center gap-1 bg-white border border-[#E8E4DC] p-1.5 rounded-full shadow-sm">
             <button className="px-6 py-2 bg-[#800020] text-white text-sm font-bold rounded-full shadow-md transition-all">Monthly</button>
             <button className="px-6 py-2 text-[#111111] bg-transparent hover:bg-gray-50 text-sm font-bold rounded-full flex items-center gap-1.5 transition-all">
               Yearly <span className="text-[10px] text-[#168A5B] font-extrabold uppercase tracking-wide">Save 20%</span>
             </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left max-w-[1000px] mx-auto items-center">
          
          {/* Free */}
          <div className="bg-[#FAF8F3] border border-[#E8E4DC] p-6 lg:p-7 rounded-[24px] shadow-sm flex flex-col h-full transform transition-transform hover:-translate-y-1">
            <div className="w-10 h-10 rounded-full bg-[#E8E4DC] flex items-center justify-center mb-4">
              <User className="w-5 h-5 text-[#5A5A5A]" />
            </div>
            <h3 className="text-[22px] font-bold text-[#111111] mb-1">Free</h3>
            <p className="text-[13px] text-[#5A5A5A] font-medium mb-4">For individuals exploring AI marketing.</p>
            <div className="text-[40px] font-bold text-[#111111] mb-5 leading-none tracking-tight">₹0<span className="text-sm text-[#858585] font-normal">/mo</span></div>
            <Button className="w-full h-10 bg-transparent border border-[#111111] text-[#111111] hover:bg-[#111111] hover:text-white font-bold rounded-xl shadow-sm transition-colors text-sm" onClick={() => window.dispatchEvent(new Event('open-auth-signup'))}>
              Get Started &rarr;
            </Button>
            <ul className="space-y-3.5 text-[13px] font-semibold text-[#5A5A5A] mt-6 pt-5 border-t border-[#E8E4DC]">
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Limited Features</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> 1 Workspace</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Core Analytics</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Basic AI Generation</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Community Support</li>
            </ul>
          </div>
          
          {/* Pro - Highlighted */}
          <div className="bg-[#FAF8F3] border-2 border-[#800020] p-6 lg:p-7 rounded-[24px] shadow-xl flex flex-col relative overflow-hidden transform md:-translate-y-4 h-[calc(100%+16px)] z-10 transition-transform hover:-translate-y-6">
            <div className="absolute top-4 right-4 bg-[#F5E6E8] text-[#800020] text-[9px] font-extrabold uppercase tracking-widest px-2.5 py-1.5 rounded-full flex items-center gap-1.5 shadow-sm">
              <Crown className="w-3 h-3" /> MOST POPULAR
            </div>
            <div className="w-10 h-10 rounded-full bg-[#F5E6E8] flex items-center justify-center mb-4">
              <Zap className="w-5 h-5 text-[#800020]" />
            </div>
            <h3 className="text-[22px] font-bold text-[#111111] mb-1">Pro</h3>
            <p className="text-[13px] text-[#5A5A5A] font-medium mb-4 pr-16">For marketing teams scaling operations.</p>
            <div className="text-[40px] font-bold text-[#111111] mb-5 leading-none tracking-tight">₹1999<span className="text-sm text-[#858585] font-normal">/mo</span></div>
            <Button className="w-full h-10 bg-[#800020] hover:bg-[#5C0017] text-white font-bold rounded-xl shadow-md border-none text-sm transition-colors" onClick={() => window.dispatchEvent(new Event('open-auth-signup'))}>
              Get Pro &rarr;
            </Button>
            <ul className="space-y-3.5 text-[13px] font-semibold text-[#5A5A5A] mt-6 pt-5 border-t border-[#E8E4DC]">
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Full Execution Loop</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Specialized Agents</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> AI CMO Access</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Unlimited Brands</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Advanced Analytics</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Priority Support</li>
            </ul>
          </div>

          {/* Custom */}
          <div className="bg-[#FAF8F3] border border-[#E8E4DC] p-6 lg:p-7 rounded-[24px] shadow-sm flex flex-col h-full transform transition-transform hover:-translate-y-1">
            <div className="w-10 h-10 rounded-full bg-[#E8E4DC] flex items-center justify-center mb-4">
              <Building2 className="w-5 h-5 text-[#5A5A5A]" />
            </div>
            <h3 className="text-[22px] font-bold text-[#111111] mb-1">Custom</h3>
            <p className="text-[13px] text-[#5A5A5A] font-medium mb-4">Tailored to your enterprise requirements.</p>
            <div className="text-[40px] font-bold text-[#111111] mb-5 leading-none tracking-tight">Custom</div>
            <Button className="w-full h-10 bg-transparent border border-[#111111] text-[#111111] hover:bg-[#111111] hover:text-white font-bold rounded-xl shadow-sm transition-colors text-sm" onClick={() => window.dispatchEvent(new Event('open-auth-signup'))}>
              Contact Sales &rarr;
            </Button>
            <ul className="space-y-3.5 text-[13px] font-semibold text-[#5A5A5A] mt-6 pt-5 border-t border-[#E8E4DC]">
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Unlimited Workspaces</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Custom Agents & Integrations</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Dedicated Support Manager</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> SSO & Advanced RBAC</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> Custom Deployment Options</li>
              <li className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0"><Check className="w-3 h-3" strokeWidth={3} /></div> SLA & Enterprise Support</li>
            </ul>
          </div>

        </div>
      </div>
    </section>
  )
}

export function FAQSection() {
  return (
    <section className="py-32 px-6 lg:px-8 bg-white/60 backdrop-blur-sm border-y border-[#E8E4DC]">
      <div className="max-w-[800px] mx-auto space-y-16">
        <div>
          <h2 className="text-[40px] md:text-[48px] font-bold tracking-tight text-center text-[#111111] leading-[1.1]">
            Frequently Asked Questions
          </h2>
        </div>
        <div className="space-y-4">
          
          <div>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">What is StandBharat?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
              <div className="mt-4 text-[#5A5A5A] font-medium leading-relaxed hidden">
                StandBharat is an AI marketing operating system...
              </div>
            </div>
          </div>
          
          <div>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">How is StandBharat different from an AI writing tool?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
              <div className="mt-4 text-[#5A5A5A] font-medium leading-relaxed hidden">
                Writing tools just generate text. StandBharat is an operating system. It ingests your analytics, finds opportunities, directs specialized agents to create content matching your brand, and manages the entire approval and publishing workflow.
              </div>
            </div>
          </div>

          <div>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">How does Brand Brain work?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
            </div>
          </div>

          <div>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">Can I control what AI executes?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
            </div>
          </div>

          <div>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">Can StandBharat publish content?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
            </div>
          </div>

          <div>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">What integrations are supported?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
            </div>
          </div>

          <div>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">How does pricing work?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  )
}

export function FinalCTA() {
  return (
    <section className="py-16 px-6 lg:px-8 bg-[#0a0a0a] text-center relative overflow-hidden">
      
      {/* Decorative background curve */}
      <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
         <svg width="100%" height="100%" viewBox="0 0 1440 600" fill="none" xmlns="http://www.w3.org/2000/svg" className="opacity-30">
            <path d="M-200 600 C 400 -100, 1040 -100, 1640 600" stroke="#800020" strokeWidth="1.5"/>
            <path d="M-200 620 C 400 -80, 1040 -80, 1640 620" stroke="#800020" strokeWidth="0.5" strokeOpacity="0.5"/>
         </svg>
      </div>

      {/* Dotted grid left */}
      <div className="absolute top-[20%] left-[10%] opacity-20 pointer-events-none hidden lg:block">
         <svg width="80" height="60" viewBox="0 0 80 60" fill="none">
            <circle cx="5" cy="5" r="1" fill="#fff" />
            <circle cx="20" cy="5" r="1" fill="#fff" />
            <circle cx="35" cy="5" r="1" fill="#fff" />
            <circle cx="50" cy="5" r="1" fill="#fff" />
            
            <circle cx="5" cy="20" r="1" fill="#fff" />
            <circle cx="20" cy="20" r="1" fill="#fff" />
            <circle cx="35" cy="20" r="1" fill="#fff" />
            <circle cx="50" cy="20" r="1" fill="#fff" />
            
            <circle cx="5" cy="35" r="1" fill="#fff" />
            <circle cx="20" cy="35" r="1" fill="#fff" />
            <circle cx="35" cy="35" r="1" fill="#fff" />
            <circle cx="50" cy="35" r="1" fill="#fff" />
         </svg>
      </div>

      {/* Dotted grid right */}
      <div className="absolute top-[15%] right-[5%] opacity-20 pointer-events-none hidden lg:block">
         <svg width="80" height="60" viewBox="0 0 80 60" fill="none">
            <circle cx="5" cy="5" r="1" fill="#fff" />
            <circle cx="20" cy="5" r="1" fill="#fff" />
            <circle cx="35" cy="5" r="1" fill="#fff" />
            
            <circle cx="5" cy="20" r="1" fill="#fff" />
            <circle cx="20" cy="20" r="1" fill="#fff" />
            <circle cx="35" cy="20" r="1" fill="#fff" />
            
            <circle cx="5" cy="35" r="1" fill="#fff" />
            <circle cx="20" cy="35" r="1" fill="#fff" />
            <circle cx="35" cy="35" r="1" fill="#fff" />
         </svg>
      </div>
      
      <div className="max-w-[1200px] mx-auto relative z-10">
        
        {/* Badge */}
        <div className="flex justify-center mb-8">
           <div className="inline-flex items-center px-5 py-1.5 rounded-full border border-[#800020]/30 bg-[#800020]/10 text-[#FF7A85] text-[10px] font-bold tracking-[0.2em] uppercase">
              All-in-one AI Marketing OS
           </div>
        </div>

        {/* Heading */}
        <div className="mb-6">
          <h2 className="text-[48px] md:text-[64px] font-extrabold tracking-tight text-white leading-[1.05]">
            Build a marketing system<br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF7A85] to-[#B3002D]">that gets smarter</span><br/>
            with every cycle.
          </h2>
        </div>
        
        {/* Subtitle */}
        <div className="mb-10">
          <p className="text-lg md:text-xl text-[#A9A4A0] font-medium max-w-2xl mx-auto leading-relaxed">
            Bring your brand, strategy, AI agents, execution and learning into one connected system — built to help you grow continuously.
          </p>
        </div>
        
        {/* Button */}
        <div className="mb-12">
          <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-signup')) }}>
            <Button size="lg" className="h-12 px-8 text-base bg-[#800020] text-white hover:bg-[#6A001A] rounded-lg font-bold border-none shadow-[0_0_20px_-5px_#800020]">
              Get Started &rarr;
            </Button>
          </Link>
        </div>

        {/* 5 Column Feature Row */}
        <div className="flex flex-col md:flex-row items-start justify-center gap-8 md:gap-0 border-t border-white/5 pt-10">
          
          <div className="flex-1 flex flex-col items-center text-center px-4 md:border-r border-white/5 relative">
            <div className="w-12 h-12 rounded-2xl bg-[#800020]/20 flex items-center justify-center mb-4">
              <Brain className="w-5 h-5 text-[#FF7A85]" />
            </div>
            <h4 className="text-white text-[13px] font-bold mb-1.5">Understand</h4>
            <p className="text-[#858585] text-xs font-medium leading-relaxed max-w-[160px]">Uses your brand, data and real-time insights.</p>
          </div>
          
          <div className="flex-1 flex flex-col items-center text-center px-4 md:border-r border-white/5 relative">
            <div className="w-12 h-12 rounded-2xl bg-[#800020]/20 flex items-center justify-center mb-4">
              <Target className="w-5 h-5 text-[#FF7A85]" />
            </div>
            <h4 className="text-white text-[13px] font-bold mb-1.5">Find Opportunities</h4>
            <p className="text-[#858585] text-xs font-medium leading-relaxed max-w-[160px]">Identifies what matters across all channels.</p>
          </div>

          <div className="flex-1 flex flex-col items-center text-center px-4 md:border-r border-white/5 relative">
            <div className="w-12 h-12 rounded-2xl bg-[#800020]/20 flex items-center justify-center mb-4">
              <Zap className="w-5 h-5 text-[#FF7A85]" />
            </div>
            <h4 className="text-white text-[13px] font-bold mb-1.5">Execute with AI Agents</h4>
            <p className="text-[#858585] text-xs font-medium leading-relaxed max-w-[160px]">Creates content, campaigns and actions for you.</p>
          </div>

          <div className="flex-1 flex flex-col items-center text-center px-4 md:border-r border-white/5 relative">
            <div className="w-12 h-12 rounded-2xl bg-[#800020]/20 flex items-center justify-center mb-4">
              <BarChart2 className="w-5 h-5 text-[#FF7A85]" />
            </div>
            <h4 className="text-white text-[13px] font-bold mb-1.5">Measure & Learn</h4>
            <p className="text-[#858585] text-xs font-medium leading-relaxed max-w-[160px]">Tracks performance and gets smarter over time.</p>
          </div>

          <div className="flex-1 flex flex-col items-center text-center px-4 relative">
            <div className="w-12 h-12 rounded-2xl bg-[#800020]/20 flex items-center justify-center mb-4">
              <TrendingUp className="w-5 h-5 text-[#FF7A85]" />
            </div>
            <h4 className="text-white text-[13px] font-bold mb-1.5">Grow Continuously</h4>
            <p className="text-[#858585] text-xs font-medium leading-relaxed max-w-[160px]">Turns insights into compounding results.</p>
          </div>

        </div>

      </div>
    </section>
  )
}



