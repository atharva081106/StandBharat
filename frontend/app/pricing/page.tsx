"use client"
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { MarketingNavbar, MarketingFooter } from '@/components/landing/navigation'

export default function Pricing() {
  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3]">
      <MarketingNavbar />
      
      <main className="flex-1 flex flex-col items-center pt-24 pb-32 px-6">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#F5E6E8] text-[#800020] text-sm font-bold mb-6">
            <div className="w-1.5 h-1.5 rounded-full bg-[#800020] animate-pulse" />
            Simple Pricing
          </div>
          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight text-[#111111] mb-6 leading-tight">
            An entire marketing team, <br/> priced for scale.
          </h1>
          <p className="text-xl text-[#5A5A5A] font-medium leading-relaxed">
            Start for free, upgrade when your AI team needs more firepower.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full">
           {/* Starter Tier */}
           <div className="bg-white p-10 rounded-[24px] border border-[#E8E4DC] shadow-sm flex flex-col">
             <h3 className="text-2xl font-bold text-[#111111]">Starter</h3>
             <p className="text-[#858585] mt-2 text-sm font-medium h-10">Basic AI agents for early stage projects.</p>
             <div className="my-8">
               <p className="text-[48px] font-bold text-[#111111] leading-none">Free</p>
             </div>
             
             <ul className="space-y-4 mb-10 flex-1">
               {['1 Active Agent', 'Basic workflow automation', 'Community support', 'Standard response times'].map((feature, i) => (
                 <li key={i} className="flex items-start gap-3">
                   <div className="w-5 h-5 rounded-full bg-[#FAF8F3] flex items-center justify-center shrink-0 mt-0.5">
                     <svg className="w-3 h-3 text-[#111111]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                   </div>
                   <span className="text-sm font-bold text-[#5A5A5A]">{feature}</span>
                 </li>
               ))}
             </ul>
             <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-signup')) }} className="mt-auto">
               <Button className="w-full h-12 bg-white hover:bg-[#FAF8F3] text-[#111111] border border-[#E8E4DC] font-bold text-base rounded-xl transition-colors shadow-none">Get Started</Button>
             </Link>
           </div>

           {/* Growth Tier */}
           <div className="bg-[#111111] p-10 rounded-[24px] shadow-2xl relative flex flex-col transform md:-translate-y-4">
             <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-[#800020] text-white px-4 py-1.5 text-xs font-bold uppercase tracking-widest rounded-full border-4 border-[#FAF8F3]">
               Most Popular
             </div>
             <h3 className="text-2xl font-bold text-white">Growth</h3>
             <p className="text-[#858585] mt-2 text-sm font-medium h-10">Full autonomous marketing team.</p>
             <div className="my-8 flex items-baseline gap-2">
               <p className="text-[48px] font-bold text-white leading-none">&#8377;4,999</p>
               <span className="text-[#858585] font-bold">/mo</span>
             </div>
             
             <ul className="space-y-4 mb-10 flex-1">
               {['Unlimited Agents', 'Advanced analytics & reporting', 'Priority execution queue', 'Custom brand voice models', 'Premium integrations'].map((feature, i) => (
                 <li key={i} className="flex items-start gap-3">
                   <div className="w-5 h-5 rounded-full bg-[#800020] flex items-center justify-center shrink-0 mt-0.5">
                     <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                   </div>
                   <span className="text-sm font-bold text-white/90">{feature}</span>
                 </li>
               ))}
             </ul>
             <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-signup')) }} className="mt-auto">
               <Button className="w-full h-12 bg-[#800020] hover:bg-[#5C0017] text-white font-bold text-base rounded-xl transition-colors border-none shadow-sm shadow-[#800020]/20">Start 14-Day Free Trial</Button>
             </Link>
           </div>

           {/* Enterprise Tier */}
           <div className="bg-white p-10 rounded-[24px] border border-[#E8E4DC] shadow-sm flex flex-col">
             <h3 className="text-2xl font-bold text-[#111111]">Enterprise</h3>
             <p className="text-[#858585] mt-2 text-sm font-medium h-10">Dedicated models and SLAs for large teams.</p>
             <div className="my-8">
               <p className="text-[48px] font-bold text-[#111111] leading-none">Custom</p>
             </div>
             
             <ul className="space-y-4 mb-10 flex-1">
               {['Dedicated compute cluster', 'SSO & Advanced Security', 'Custom integrations', '24/7 Phone Support', 'Dedicated Success Manager'].map((feature, i) => (
                 <li key={i} className="flex items-start gap-3">
                   <div className="w-5 h-5 rounded-full bg-[#FAF8F3] flex items-center justify-center shrink-0 mt-0.5">
                     <svg className="w-3 h-3 text-[#111111]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                   </div>
                   <span className="text-sm font-bold text-[#5A5A5A]">{feature}</span>
                 </li>
               ))}
             </ul>
             <Link href="#" className="mt-auto">
               <Button className="w-full h-12 bg-white hover:bg-[#FAF8F3] text-[#111111] border border-[#E8E4DC] font-bold text-base rounded-xl transition-colors shadow-none">Contact Sales</Button>
             </Link>
           </div>
        </div>
      </main>
      
      <MarketingFooter />
    </div>
  )
}

