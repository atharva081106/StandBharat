import { MarketingNavbar, MarketingFooter } from '@/components/landing/navigation'
import { HeroSection, CapabilityStrip } from '@/components/landing/hero'

import { WorkflowFlow } from '@/components/landing/flow'
import { AiCmoSection } from '@/components/landing/features'
import { PricingSection, FAQSection, FinalCTA } from '@/components/landing/conversion'
import { Metadata } from 'next'
import { Outfit } from 'next/font/google'

const outfit = Outfit({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'StandBharat — AI Marketing Operating System',
  description: 'StandBharat connects your brand intelligence, AI CMO, specialized agents, content, execution and performance into one continuous marketing system.',
}

import { SmoothScroll } from '@/components/lenis-provider'

export default function LandingPage() {
  return (
    <div className={`min-h-screen flex flex-col bg-[#FAF8F3] selection:bg-[#800020] selection:text-white ${outfit.className}`}>
      <SmoothScroll />
      {/* Global Background Graphics */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-[#800020] blur-[150px] opacity-[0.05] mix-blend-multiply animate-pulse" style={{ animationDuration: '8s' }} />
        <div className="absolute top-[30%] right-[-5%] w-[40%] h-[50%] rounded-full bg-[#5C0017] blur-[120px] opacity-[0.05] mix-blend-multiply animate-pulse" style={{ animationDuration: '12s' }} />
        <div className="absolute bottom-[-10%] left-[20%] w-[50%] h-[50%] rounded-full bg-[#111111] blur-[150px] opacity-[0.03] mix-blend-multiply" />
        <div className="absolute inset-0 bg-[url('https://res.cloudinary.com/djp1xhexg/image/upload/v1727788414/grid_czvjio.svg')] bg-center opacity-30" style={{ maskImage: 'linear-gradient(to bottom, rgba(0,0,0,1), rgba(0,0,0,0.2) 100%)', WebkitMaskImage: 'linear-gradient(to bottom, rgba(0,0,0,1), rgba(0,0,0,0.2) 100%)' }} />
        
        {/* Floating Geometric Particles */}
        <div className="absolute top-[15%] left-[8%] w-8 h-8 border-[2px] border-[#800020]/20 rounded-full animate-[spin_10s_linear_infinite]" style={{ borderStyle: 'dashed' }} />
        <div className="absolute top-[45%] right-[12%] w-4 h-4 bg-[#800020]/10 rounded-sm rotate-45 animate-[pulse_3s_ease-in-out_infinite]" />
        <div className="absolute bottom-[25%] left-[15%] w-12 h-12 border border-[#111111]/10 rounded-full" />
        <div className="absolute top-[65%] left-[45%] w-2 h-2 rounded-full bg-[#800020]/20" />
      </div>
      <MarketingNavbar />
      <main className="flex-1 relative z-10">
        <HeroSection />
        <CapabilityStrip />
        <WorkflowFlow />
        <AiCmoSection />
        <PricingSection />
        <FAQSection />
        <FinalCTA />
      </main>
      <MarketingFooter />
    </div>
  )
}


