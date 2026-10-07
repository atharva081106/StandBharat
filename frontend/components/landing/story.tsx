'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useState } from 'react'
import { ScrollReveal } from '@/components/ui/scroll-reveal'

const CHAOS_TOOLS = [
  { label: 'Analytics', angle: 90 },
  { label: 'Ad Platforms', angle: 45 },
  { label: 'Content Tools', angle: 135 },
  { label: 'Social Media', angle: 0 },
  { label: 'Email Tools', angle: 180 },
  { label: 'Spreadsheets', angle: 225 },
  { label: 'CRM', angle: 315 },
  { label: 'AI Chatbots', angle: 270 },
]

function ChaosOrb() {
  const r = 160
  return (
    <div className="relative w-[420px] h-[420px] flex items-center justify-center mx-auto">
      {CHAOS_TOOLS.map((tool) => {
        const rad = (tool.angle * Math.PI) / 180
        const x = 50 + (r / 420) * 100 * Math.cos(rad)
        const y = 50 - (r / 420) * 100 * Math.sin(rad)
        return (
          <div
            key={tool.label}
            className="absolute bg-white border border-[#E8E4DC] px-3 py-1.5 rounded-lg text-[11px] font-bold text-[#5A5A5A] shadow-sm select-none z-10"
            style={{ left: `${x}%`, top: `${y}%`, transform: 'translate(-50%,-50%)' }}
          >
            {tool.label}
          </div>
        )
      })}

      <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 0 }}>
        {CHAOS_TOOLS.map((tool) => {
          const rad = (tool.angle * Math.PI) / 180
          const ex = 50 + (r / 420) * 100 * Math.cos(rad)
          const ey = 50 - (r / 420) * 100 * Math.sin(rad)
          return (
            <line
              key={tool.label}
              x1="50%" y1="50%"
              x2={`${ex}%`} y2={`${ey}%`}
              stroke="#D0CCC3" strokeWidth="1.5" strokeDasharray="5 4"
            />
          )
        })}
      </svg>

      <div className="relative z-20 bg-[#111111] text-white rounded-2xl px-7 py-5 text-center shadow-2xl max-w-[180px]">
        <div className="text-xs font-extrabold uppercase tracking-wider leading-relaxed">
          YOUR TEAM<br />
          <span className="text-[#800020]">BECOMES THE</span><br />
          INTEGRATION LAYER.
        </div>
      </div>
    </div>
  )
}

export function ProblemSection() {
  return (
    <section className="py-28 px-6 lg:px-8 bg-transparent border-t border-[#E8E4DC]" id="problem">
      <div className="max-w-[1400px] mx-auto">
        <ScrollReveal>
          <div className="text-[11px] font-bold uppercase tracking-[0.22em] text-[#858585] mb-8">
            THE PROBLEM
          </div>
        </ScrollReveal>
        <div className="flex flex-col lg:flex-row gap-16 lg:gap-24 items-center">
          <div className="w-full lg:w-[42%] space-y-10">
            <ScrollReveal delay={0.1}>
              <h2 className="text-[44px] md:text-[58px] font-extrabold tracking-tight text-[#111111] leading-[1.05]">
                Marketing wasn&apos;t built<br/>to work this way.
              </h2>
            </ScrollReveal>
            <ScrollReveal delay={0.2}>
              <p className="text-lg text-[#5A5A5A] leading-relaxed max-w-md font-medium">
                Businesses rely on multiple disconnected tools, manual processes and scattered data. Teams spend more time coordinating marketing than driving growth.
              </p>
            </ScrollReveal>
            <ScrollReveal delay={0.3}>
              <div className="grid grid-cols-3 gap-6 pt-8 border-t border-[#E8E4DC]">
                <div>
                  <div className="text-[36px] font-extrabold text-[#111111] leading-none mb-2">10+</div>
                  <div className="text-xs font-bold text-[#858585] uppercase tracking-wider">Tools to manage</div>
                </div>
                <div>
                  <div className="text-[36px] font-extrabold text-[#111111] leading-none mb-2">60%</div>
                  <div className="text-xs font-bold text-[#858585] uppercase tracking-wider">Time on coordination</div>
                </div>
                <div>
                  <div className="text-[36px] font-extrabold text-[#800020] leading-none mb-2">LOWER</div>
                  <div className="text-xs font-bold text-[#858585] uppercase tracking-wider">Marketing impact</div>
                </div>
              </div>
              <p className="text-[10px] text-[#B0AB9E] uppercase tracking-widest font-bold mt-10">
                * Typical marketing workflow
              </p>
            </ScrollReveal>
          </div>
          <div className="w-full lg:w-[58%] flex justify-center">
            <ScrollReveal delay={0.4} className="w-full max-w-[560px]">
              <div className="bg-white border border-[#E8E4DC] rounded-[28px] p-10 shadow-xl shadow-black/5 w-full flex items-center justify-center min-h-[460px]">
                <ChaosOrb />
              </div>
            </ScrollReveal>
          </div>
        </div>
      </div>
    </section>
  )
}

// ─── Marketing Loop ────────────────────────────────────────────────────────────

const LOOP_STEPS = [
  { label: 'Understand\nYour Brand', angle: 90 },
  { label: 'Find\nOpportunities', angle: 39 },
  { label: 'Create Strategy\n& Content', angle: -12 },
  { label: 'Get\nApproval', angle: -64 },
  { label: 'Publish Across\nChannels', angle: -116 },
  { label: 'Measure\nPerformance', angle: -168 },
  { label: 'Learn &\nOptimize', angle: 141 },
]

export function MarketingLoop() {
  const [active, setActive] = useState<number | null>(null)
  const r = 200

  return (
    <section className="py-28 px-6 lg:px-8 bg-white/60 backdrop-blur-sm border-y border-[#E8E4DC]" id="how-it-works">
      <div className="max-w-[1400px] mx-auto flex flex-col lg:flex-row gap-16 lg:gap-24 items-center">
        <div className="w-full lg:w-[40%] space-y-8">
          <ScrollReveal delay={0}>
            <div className="text-[11px] font-bold uppercase tracking-[0.22em] text-[#858585]">
              THE SOLUTION
            </div>
          </ScrollReveal>
          <ScrollReveal delay={0.1}>
            <h2 className="text-[44px] md:text-[58px] font-extrabold tracking-tight text-[#111111] leading-[1.05]">
              One continuous<br/>marketing loop.
            </h2>
          </ScrollReveal>
          <ScrollReveal delay={0.2}>
            <p className="text-lg text-[#5A5A5A] leading-relaxed font-medium">
              StandBharat connects the entire marketing lifecycle from insight to execution, with an AI CMO orchestrating specialized agents, strategy and decisions.
            </p>
          </ScrollReveal>
          <ScrollReveal delay={0.3}>
            <div className="space-y-1 pt-2">
              {LOOP_STEPS.map((step, i) => (
                <div
                  key={i}
                  onMouseEnter={() => setActive(i)}
                  onMouseLeave={() => setActive(null)}
                  className={`flex items-center gap-3 rounded-xl px-4 py-2.5 cursor-default transition-all duration-200 ${active === i ? 'bg-[#FAF8F3] border border-[#E8E4DC]' : 'border border-transparent'}`}
                >
                  <div className={`w-2 h-2 rounded-full shrink-0 transition-colors duration-200 ${active === i ? 'bg-[#800020]' : 'bg-[#D0CCC3]'}`}></div>
                  <span className={`text-sm font-semibold transition-colors duration-200 ${active === i ? 'text-[#111111]' : 'text-[#858585]'}`}>
                    {step.label.replace('\n', ' ')}
                  </span>
                </div>
              ))}
            </div>
            <Link href="#product">
              <Button size="lg" className="h-12 px-8 text-base bg-[#111111] text-white hover:bg-[#171717] rounded-xl font-semibold mt-2">
                See How It Works →
              </Button>
            </Link>
          </ScrollReveal>
        </div>

        <div className="w-full lg:w-[60%] flex justify-center">
          <ScrollReveal delay={0.4}>
            <div className="relative w-[480px] h-[480px] flex items-center justify-center">
              <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 480 480">
                <circle cx="240" cy="240" r={r} fill="none" stroke="#E8E4DC" strokeWidth="1.5" strokeDasharray="8 6" />
              </svg>
              {LOOP_STEPS.map((step, i) => {
                const rad = (step.angle * Math.PI) / 180
                const x = 240 + r * Math.cos(rad)
                const y = 240 - r * Math.sin(rad)
                const isActive = active === i
                return (
                  <div
                    key={i}
                    onMouseEnter={() => setActive(i)}
                    onMouseLeave={() => setActive(null)}
                    className="absolute flex flex-col items-center gap-1.5 cursor-default transition-all duration-200 z-10"
                    style={{ left: x, top: y, transform: 'translate(-50%,-50%)' }}
                  >
                    <div className={`w-3 h-3 rounded-full border-2 transition-all duration-200 ${isActive ? 'bg-[#800020] border-[#800020] scale-125' : 'bg-white border-[#D0CCC3]'}`}></div>
                    <div className={`bg-white border rounded-xl px-3 py-1.5 text-center text-[10px] font-bold leading-tight shadow-sm transition-all duration-200 whitespace-nowrap ${isActive ? 'border-[#800020] text-[#800020] shadow-md -translate-y-1' : 'border-[#E8E4DC] text-[#5A5A5A]'}`}>
                      {step.label.split('\n').map((line, j) => <div key={j}>{line}</div>)}
                    </div>
                  </div>
                )
              })}
              <div className="relative z-20 w-32 h-32 rounded-full bg-white border-2 border-[#800020] shadow-xl shadow-[#800020]/10 flex flex-col items-center justify-center text-center gap-1 hover:scale-105 transition-transform duration-300 cursor-default">
                <div className="w-4 h-4 rounded-full bg-[#800020]"></div>
                <span className="text-xs font-extrabold text-[#111111] tracking-tight leading-tight">StandBharat</span>
                <span className="text-[9px] text-[#858585] font-semibold uppercase tracking-wider">AI CMO</span>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  )
}

// ─── Differentiation Section ───────────────────────────────────────────────────

const DIFF_CARDS = [
  {
    title: 'Unified System',
    desc: 'Everything connected in one place. No more stitching tools together manually.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>
      </svg>
    ),
  },
  {
    title: 'Built for Real Businesses',
    desc: 'Not just content generation. Real marketing outcomes with measurable revenue attribution.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
      </svg>
    ),
  },
  {
    title: 'Human in Control',
    desc: 'AI recommends, you decide and approve. Always in command of every action.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
      </svg>
    ),
  },
  {
    title: 'Learns Over Time',
    desc: 'Every campaign creates richer context. Every decision makes the next one smarter.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
      </svg>
    ),
  },
]

export function DifferentiationSection() {
  return (
    <section className="py-28 px-6 lg:px-8 bg-[#111111] text-white">
      <div className="max-w-[1400px] mx-auto space-y-16">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
          <div className="space-y-4 max-w-xl">
            <ScrollReveal delay={0}>
              <div className="text-[11px] font-bold uppercase tracking-[0.22em] text-[#858585]">
                WHY STANDBHARAT
              </div>
            </ScrollReveal>
            <ScrollReveal delay={0.1}>
              <h2 className="text-[40px] md:text-[52px] font-extrabold tracking-tight leading-[1.05]">
                More than tools.<br/>A smarter way to market.
              </h2>
            </ScrollReveal>
          </div>
          <ScrollReveal delay={0.2}>
            <p className="text-[#858585] text-lg font-medium max-w-sm leading-relaxed">
              An AI-native system that thinks, acts, and learns — so your team can focus on what matters.
            </p>
          </ScrollReveal>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {DIFF_CARDS.map((card, i) => (
            <ScrollReveal delay={0.1 * i} key={i}>
              <div className="group p-8 rounded-[20px] bg-[#181818] border border-white/[0.08] hover:border-[#800020]/60 hover:bg-[#1C1214] transition-all duration-300 cursor-default h-full">
                <div className="w-11 h-11 rounded-xl bg-[#800020]/15 flex items-center justify-center text-[#F5E6E8] mb-7 group-hover:bg-[#800020]/25 transition-colors duration-300">
                  {card.icon}
                </div>
                <h3 className="text-base font-bold mb-3 text-white">{card.title}</h3>
                <p className="text-sm text-[#858585] leading-relaxed font-medium">{card.desc}</p>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  )
}

