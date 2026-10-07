"use client"
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ScrollReveal } from '@/components/ui/scroll-reveal'

export function UseCasesSection() {
  return (
    <section className="py-32 px-6 lg:px-8 bg-white/60 backdrop-blur-sm border-y border-[#E8E4DC]">
      <div className="max-w-[1400px] mx-auto space-y-16">
        <ScrollReveal delay={0}>
          <div className="text-center space-y-4">
            <h2 className="text-[40px] md:text-[48px] font-bold tracking-tight text-[#111111] leading-[1.1]">
              Built for every<br/>marketing leader.
            </h2>
            <p className="text-xl text-[#5A5A5A] font-medium max-w-2xl mx-auto">
              Whether you&apos;re a founder, marketing lead or growth team, StandBharat adapts to your goals.
            </p>
          </div>
        </ScrollReveal>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <ScrollReveal delay={0.1}>
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
          </ScrollReveal>
          <ScrollReveal delay={0.2}>
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
          </ScrollReveal>
          <ScrollReveal delay={0.3}>
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
          </ScrollReveal>
          <ScrollReveal delay={0.4}>
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
          </ScrollReveal>
        </div>
      </div>
    </section>
  )
}

export function PricingSection() {
  return (
    <section className="py-32 px-6 lg:px-8 bg-transparent" id="pricing">
      <div className="max-w-[1200px] mx-auto text-center space-y-16">
        
        <ScrollReveal delay={0}>
          <div className="space-y-6">
            <h2 className="text-[40px] md:text-[56px] font-bold tracking-tight text-[#111111] leading-[1.1]">
              Pricing
            </h2>
            <p className="text-xl text-[#5A5A5A] font-medium">
              Everything you need to run an autonomous marketing system.
            </p>
            
            <div className="inline-flex items-center gap-2 bg-white border border-[#E8E4DC] p-1 rounded-lg">
               <button className="px-4 py-2 bg-[#FAF8F3] text-[#111111] text-sm font-bold rounded-md shadow-sm border border-[#E8E4DC]">Monthly</button>
               <button className="px-4 py-2 text-[#5A5A5A] text-sm font-bold rounded-md">Yearly <span className="text-[10px] text-[#168A5B] uppercase tracking-wider ml-1">Save 20%</span></button>
            </div>
          </div>
        </ScrollReveal>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
          
          {/* Free */}
          <ScrollReveal delay={0.1}>
            <div className="bg-white border border-[#E8E4DC] p-8 rounded-[24px] shadow-sm flex flex-col relative h-full">
              <h3 className="text-xl font-bold text-[#111111] mb-2">Free</h3>
              <p className="text-sm text-[#5A5A5A] font-medium mb-6">For individuals exploring AI marketing.</p>
              <div className="text-[48px] font-bold text-[#111111] mb-8 leading-none tracking-tight">₹0<span className="text-lg text-[#858585] font-normal">/mo</span></div>
              <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-signup')) }}>
                <Button className="w-full h-12 bg-white border border-[#E8E4DC] text-[#111111] hover:bg-[#FAF8F3] font-bold rounded-xl shadow-sm">Get Started for Free</Button>
              </Link>
              <ul className="space-y-4 text-sm font-medium text-[#5A5A5A] mt-8 pt-8 border-t border-[#E8E4DC]">
                <li className="flex items-center gap-3"><span className="text-[#111111] font-bold">&check;</span> Limited Features</li>
                <li className="flex items-center gap-3"><span className="text-[#111111] font-bold">&check;</span> 1 Workspace</li>
                <li className="flex items-center gap-3"><span className="text-[#111111] font-bold">&check;</span> Core Analytics</li>
                <li className="flex items-center gap-3"><span className="text-[#111111] font-bold">&check;</span> Basic AI Generation</li>
              </ul>
            </div>
          </ScrollReveal>
          
          {/* Pro - Highlighted */}
          <ScrollReveal delay={0.2}>
            <div className="bg-white border-2 border-[#800020] p-8 rounded-[24px] shadow-xl flex flex-col relative overflow-hidden transform md:-translate-y-4 h-[calc(100%+16px)]">
              <div className="absolute top-0 inset-x-0 h-1 bg-[#800020]"></div>
              <div className="absolute top-4 right-4 bg-[#F5E6E8] text-[#5C0017] text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full">Most Popular</div>
              
              <h3 className="text-xl font-bold text-[#111111] mb-2">Pro</h3>
              <p className="text-sm text-[#5A5A5A] font-medium mb-6">For marketing teams scaling operations.</p>
              <div className="text-[48px] font-bold text-[#111111] mb-8 leading-none tracking-tight">₹1999<span className="text-lg text-[#858585] font-normal">/mo</span></div>
              <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-signup')) }}>
                <Button className="w-full h-12 bg-[#800020] hover:bg-[#5C0017] text-white font-bold rounded-xl shadow-sm border-none">Get Pro</Button>
              </Link>
              <ul className="space-y-4 text-sm font-medium text-[#5A5A5A] mt-8 pt-8 border-t border-[#E8E4DC]">
                <li className="flex items-center gap-3"><span className="text-[#800020] font-bold">&check;</span> Full Execution Loop</li>
                <li className="flex items-center gap-3"><span className="text-[#800020] font-bold">&check;</span> Specialized Agents</li>
                <li className="flex items-center gap-3"><span className="text-[#800020] font-bold">&check;</span> AI CMO Access</li>
                <li className="flex items-center gap-3"><span className="text-[#800020] font-bold">&check;</span> Unlimited Brands</li>
                <li className="flex items-center gap-3"><span className="text-[#800020] font-bold">&check;</span> Priority Support</li>
              </ul>
            </div>
          </ScrollReveal>

          {/* Custom */}
          <ScrollReveal delay={0.3}>
            <div className="bg-white border border-[#E8E4DC] p-8 rounded-[24px] shadow-sm flex flex-col relative h-full">
              <h3 className="text-xl font-bold text-[#111111] mb-2">Custom</h3>
              <p className="text-sm text-[#5A5A5A] font-medium mb-6">Tailored to your specific enterprise requirements.</p>
              <div className="text-[48px] font-bold text-[#111111] mb-8 leading-none tracking-tight">Custom</div>
              <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-signup')) }}>
                <Button className="w-full h-12 bg-white border border-[#E8E4DC] text-[#111111] hover:bg-[#FAF8F3] font-bold rounded-xl shadow-sm">Contact Sales</Button>
              </Link>
              <ul className="space-y-4 text-sm font-medium text-[#5A5A5A] mt-8 pt-8 border-t border-[#E8E4DC]">
                <li className="flex items-center gap-3"><span className="text-[#111111] font-bold">&check;</span> Unlimited Workspaces</li>
                <li className="flex items-center gap-3"><span className="text-[#111111] font-bold">&check;</span> Custom Agents & Integrations</li>
                <li className="flex items-center gap-3"><span className="text-[#111111] font-bold">&check;</span> Dedicated Support Manager</li>
                <li className="flex items-center gap-3"><span className="text-[#111111] font-bold">&check;</span> SSO & Advanced RBAC</li>
              </ul>
            </div>
          </ScrollReveal>

        </div>
      </div>
    </section>
  )
}

export function FAQSection() {
  return (
    <section className="py-32 px-6 lg:px-8 bg-white/60 backdrop-blur-sm border-y border-[#E8E4DC]">
      <div className="max-w-[800px] mx-auto space-y-16">
        <ScrollReveal delay={0}>
          <h2 className="text-[40px] md:text-[48px] font-bold tracking-tight text-center text-[#111111] leading-[1.1]">
            Frequently Asked Questions
          </h2>
        </ScrollReveal>
        <div className="space-y-4">
          
          <ScrollReveal delay={0.1}>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">What is StandBharat?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
              <div className="mt-4 text-[#5A5A5A] font-medium leading-relaxed hidden">
                StandBharat is an AI marketing operating system...
              </div>
            </div>
          </ScrollReveal>
          
          <ScrollReveal delay={0.15}>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">How is StandBharat different from an AI writing tool?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
              <div className="mt-4 text-[#5A5A5A] font-medium leading-relaxed hidden">
                Writing tools just generate text. StandBharat is an operating system. It ingests your analytics, finds opportunities, directs specialized agents to create content matching your brand, and manages the entire approval and publishing workflow.
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={0.2}>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">How does Brand Brain work?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={0.25}>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">Can I control what AI executes?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={0.3}>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">Can StandBharat publish content?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={0.35}>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">What integrations are supported?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={0.4}>
            <div className="border border-[#E8E4DC] rounded-[16px] bg-[#FAF8F3] p-6 shadow-sm cursor-pointer group hover:bg-white transition-colors">
              <div className="flex justify-between items-center">
                 <h4 className="font-bold text-[#111111] text-lg group-hover:text-[#800020] transition-colors">How does pricing work?</h4>
                 <span className="text-[#111111] text-xl font-bold">+</span>
              </div>
            </div>
          </ScrollReveal>

        </div>
      </div>
    </section>
  )
}

export function FinalCTA() {
  return (
    <section className="py-32 px-6 lg:px-8 bg-[#111111] text-center relative overflow-hidden">
      
      {/* Decorative growth curve */}
      <div className="absolute bottom-0 left-0 right-0 h-64 pointer-events-none opacity-20">
         <svg width="100%" height="100%" viewBox="0 0 1440 300" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 300C400 300 600 50 1440 50" stroke="#800020" strokeWidth="4"/>
         </svg>
      </div>

      <div className="max-w-[1000px] mx-auto space-y-10 relative z-10">
        <ScrollReveal delay={0}>
          <h2 className="text-[48px] md:text-[72px] font-extrabold tracking-tight text-white leading-[1.05]">
            Build a marketing system<br/>that gets smarter<br/>with every cycle.
          </h2>
        </ScrollReveal>
        <ScrollReveal delay={0.1}>
          <p className="text-xl text-[#858585] font-medium max-w-2xl mx-auto">
            Bring your brand, strategy, AI agents, execution and learning into one system.
          </p>
        </ScrollReveal>
        <ScrollReveal delay={0.2}>
          <div className="pt-8">
            <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-signup')) }}>
              <Button size="lg" className="h-14 px-10 text-lg bg-[#800020] text-white hover:bg-[#5C0017] rounded-xl font-bold border-none shadow-lg shadow-[#800020]/20">
                Get Started &rarr;
              </Button>
            </Link>
          </div>
        </ScrollReveal>
      </div>
    </section>
  )
}



