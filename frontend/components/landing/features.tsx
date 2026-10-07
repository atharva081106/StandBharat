import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { ScrollReveal } from '@/components/ui/scroll-reveal'

export function AiCmoSection() {
  return (
    <section className="py-32 px-6 lg:px-8 bg-[#111111] relative overflow-hidden" id="ai-cmo">
      {/* Abstract Line Art */}
      <div className="absolute inset-0 pointer-events-none opacity-30 flex items-center justify-center">
        <svg width="100%" height="100%" viewBox="0 0 1440 800" fill="none" xmlns="http://www.w3.org/2000/svg">
           <path d="M-100 400C200 400 400 100 720 100C1040 100 1200 700 1540 700" stroke="#800020" strokeWidth="2" strokeOpacity="0.5"/>
           <path d="M-100 450C200 450 400 150 720 150C1040 150 1200 750 1540 750" stroke="#800020" strokeWidth="1" strokeOpacity="0.3"/>
        </svg>
      </div>

      <div className="max-w-[1400px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative z-10">
        
        {/* Left Side */}
        <div className="space-y-12">
          <div className="space-y-6">
            <ScrollReveal delay={0}>
              <div className="text-[11px] font-bold uppercase tracking-[0.2em] text-[#800020]">
                AI CMO
              </div>
            </ScrollReveal>
            <ScrollReveal delay={0.1}>
              <h2 className="text-[40px] md:text-[56px] font-bold tracking-tight text-white leading-[1.1]">
                Meet your AI CMO.
              </h2>
            </ScrollReveal>
            <ScrollReveal delay={0.2}>
              <p className="text-xl text-[#858585] font-medium max-w-md">
                Strategic. Contextual. Actionable.<br/>
                Always on your side.
              </p>
            </ScrollReveal>
          </div>
          
          <ScrollReveal delay={0.3}>
            <div className="space-y-8">
               <div>
                  <h4 className="text-white font-bold mb-1 text-sm">UNDERSTANDS YOUR BUSINESS</h4>
                  <p className="text-[#858585] text-sm">Uses your Brand Brain and real data.</p>
               </div>
               <div>
                  <h4 className="text-white font-bold mb-1 text-sm">FINDS WHAT MATTERS</h4>
                  <p className="text-[#858585] text-sm">Identifies the highest-value opportunities.</p>
               </div>
               <div>
                  <h4 className="text-white font-bold mb-1 text-sm">COORDINATES EXECUTION</h4>
                  <p className="text-[#858585] text-sm">Works with specialized agents to get things done.</p>
               </div>
            </div>
          </ScrollReveal>
          
          <ScrollReveal delay={0.4}>
            <div className="pt-4">
               <Link href="#product">
                 <Button size="lg" className="h-12 px-8 text-base bg-[#800020] text-white hover:bg-[#5C0017] rounded-xl font-semibold border-none">
                   Talk to the AI CMO &rarr;
                 </Button>
               </Link>
            </div>
          </ScrollReveal>
        </div>
        
        {/* Right Side - Chat Mockup */}
        <div className="w-full relative">
          <ScrollReveal delay={0.4}>
            <div className="bg-[#171717] rounded-2xl border border-white/10 shadow-2xl overflow-hidden flex flex-col h-[600px]">
               <div className="h-14 border-b border-white/10 flex items-center px-6">
                  <span className="font-bold text-white text-sm">AI CMO</span>
               </div>
               
               <div className="flex-1 p-6 overflow-y-auto space-y-6 flex flex-col">
                  
                  {/* User Message */}
                  <div className="flex flex-col items-end">
                     <div className="bg-[#800020] text-white p-4 rounded-[16px] rounded-tr-[4px] max-w-[85%] text-sm font-medium shadow-sm">
                       What should we focus on this week?
                     </div>
                  </div>
                  
                  {/* AI Response */}
                  <div className="flex flex-col items-start">
                     <div className="bg-[#222222] border border-white/10 p-5 rounded-[16px] rounded-tl-[4px] max-w-[90%] shadow-sm text-sm">
                       <p className="text-white mb-4">
                         Based on your brand, audience and recent performance, I&apos;ve identified 3 high-impact opportunities.
                       </p>
                       
                       <div className="space-y-3 mb-5">
                          <div className="bg-[#111111] border border-white/5 p-3 rounded-lg">
                             <div className="text-[10px] text-[#800020] font-bold uppercase mb-1">Opportunity 1</div>
                             <div className="text-white font-medium">Improve positioning around AI-powered marketing systems</div>
                          </div>
                          <div className="bg-[#111111] border border-white/5 p-3 rounded-lg">
                             <div className="text-[10px] text-[#800020] font-bold uppercase mb-1">Opportunity 2</div>
                             <div className="text-white font-medium">Launch a thought-leadership content series</div>
                          </div>
                          <div className="bg-[#111111] border border-white/5 p-3 rounded-lg">
                             <div className="text-[10px] text-[#800020] font-bold uppercase mb-1">Opportunity 3</div>
                             <div className="text-white font-medium">Re-engage inactive audience segment</div>
                          </div>
                       </div>
                       
                       <div className="flex flex-wrap gap-2">
                         <button className="px-3 py-1.5 bg-white text-[#111111] text-xs font-semibold rounded-lg hover:bg-[#FAF8F3]">Create Strategy</button>
                         <button className="px-3 py-1.5 bg-[#333333] text-white text-xs font-semibold rounded-lg hover:bg-[#444444]">Create Content</button>
                         <button className="px-3 py-1.5 border border-white/20 text-white hover:bg-white/5 text-xs font-semibold rounded-lg">View Opportunities</button>
                       </div>
                     </div>
                  </div>
               </div>
               
               <div className="p-4 border-t border-white/10 bg-[#171717]">
                 <div className="bg-[#222222] border border-white/10 rounded-xl px-4 py-3 text-sm text-[#858585] flex items-center">
                    Ask the AI CMO anything...
                 </div>
               </div>
            </div>
          </ScrollReveal>
        </div>
        
      </div>
    </section>
  )
}

export function FeaturesThreeColumns() {
  return (
    <section className="py-32 px-6 lg:px-8 bg-white/60 backdrop-blur-sm" id="product">
      <div className="max-w-[1400px] mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Brand Brain */}
        <ScrollReveal delay={0} className="h-full">
          <div className="flex flex-col h-full bg-[#FAF8F3] border border-[#E8E4DC] rounded-[24px] overflow-hidden">
            <div className="p-8 pb-4">
              <h3 className="text-2xl font-bold text-[#111111] mb-2">Brand Brain</h3>
              <p className="text-[#5A5A5A] text-sm font-medium">Your company&apos;s intelligence foundation.</p>
            </div>
            <div className="flex-1 px-8 pb-8 pt-4">
              <div className="bg-white border border-[#E8E4DC] rounded-xl p-4 shadow-sm h-full space-y-3">
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Brand Overview</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Brand Voice</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Audience</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Products</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Positioning</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Goals</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm">
                    <span className="font-semibold text-[#111111]">Competitors</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
              </div>
            </div>
            <div className="p-8 pt-0 mt-auto">
               <Link href="#product">
                 <span className="text-[#800020] font-bold text-sm hover:text-[#5C0017]">Explore Brand Brain &rarr;</span>
               </Link>
            </div>
          </div>
        </ScrollReveal>

        {/* Specialized Agents */}
        <ScrollReveal delay={0.1} className="h-full">
          <div className="flex flex-col h-full bg-[#FAF8F3] border border-[#E8E4DC] rounded-[24px] overflow-hidden">
            <div className="p-8 pb-4">
              <h3 className="text-2xl font-bold text-[#111111] mb-2">Specialized AI Agents</h3>
              <p className="text-[#5A5A5A] text-sm font-medium">Working together for your growth.</p>
            </div>
            <div className="flex-1 px-8 pb-8 pt-4">
              <div className="bg-white border border-[#E8E4DC] rounded-xl p-4 shadow-sm h-full space-y-3">
                 <div className="p-3 border border-[#E8E4DC] bg-[#FAF8F3] rounded-lg">
                   <div className="flex justify-between items-center mb-1">
                     <span className="text-sm font-bold text-[#111111]">Analytics Agent</span>
                     <span className="text-[10px] uppercase font-bold text-[#168A5B]">Idle</span>
                   </div>
                   <div className="w-full bg-[#E8E4DC] h-1 rounded-full overflow-hidden"></div>
                 </div>
                 <div className="p-3 border border-[#E8E4DC] bg-[#FAF8F3] rounded-lg">
                   <div className="flex justify-between items-center mb-1">
                     <span className="text-sm font-bold text-[#111111]">Competitor Agent</span>
                     <span className="text-[10px] uppercase font-bold text-[#168A5B]">Idle</span>
                   </div>
                   <div className="w-full bg-[#E8E4DC] h-1 rounded-full overflow-hidden"></div>
                 </div>
                 <div className="p-3 border border-[#E8E4DC] bg-white rounded-lg shadow-sm border-l-2 border-l-[#800020]">
                   <div className="flex justify-between items-center mb-1">
                     <span className="text-sm font-bold text-[#111111]">Growth Agent</span>
                     <span className="text-[10px] uppercase font-bold text-[#800020] animate-pulse">Running</span>
                   </div>
                   <div className="w-full bg-[#E8E4DC] h-1 rounded-full overflow-hidden">
                      <div className="w-1/2 h-full bg-[#800020]"></div>
                   </div>
                 </div>
                 <div className="p-3 border border-[#E8E4DC] bg-[#FAF8F3] rounded-lg">
                   <div className="flex justify-between items-center mb-1">
                     <span className="text-sm font-bold text-[#111111]">Content Strategy Agent</span>
                   </div>
                 </div>
                 <div className="p-3 border border-[#E8E4DC] bg-[#FAF8F3] rounded-lg">
                   <div className="flex justify-between items-center mb-1">
                     <span className="text-sm font-bold text-[#111111]">Content Writer Agent</span>
                   </div>
                 </div>
              </div>
            </div>
            <div className="p-8 pt-0 mt-auto">
               <Link href="#product">
                 <span className="text-[#800020] font-bold text-sm hover:text-[#5C0017]">Meet the Agents &rarr;</span>
               </Link>
            </div>
          </div>
        </ScrollReveal>
        
        {/* Opportunities */}
        <ScrollReveal delay={0.2} className="h-full">
          <div className="flex flex-col h-full bg-[#FAF8F3] border border-[#E8E4DC] rounded-[24px] overflow-hidden">
            <div className="p-8 pb-4">
              <h3 className="text-2xl font-bold text-[#111111] mb-2 leading-tight">Don&apos;t ask AI what to do. Let it find what matters.</h3>
              <p className="text-[#5A5A5A] text-sm font-medium mt-2">Opportunity Engine</p>
            </div>
            <div className="flex-1 px-8 pb-8 pt-4">
              <div className="bg-white border border-[#E8E4DC] rounded-xl p-4 shadow-sm h-full space-y-4">
                 <div className="p-4 border border-[#E8E4DC] rounded-lg shadow-sm">
                   <h4 className="text-sm font-bold text-[#111111] mb-2">Turn high-performing content into a series</h4>
                   <div className="flex gap-3 text-[10px] font-bold uppercase tracking-wider">
                      <span className="text-[#168A5B]">High Impact</span>
                      <span className="text-[#5A5A5A]">92% Conf</span>
                      <span className="text-[#5A5A5A]">Low Effort</span>
                   </div>
                 </div>
                 <div className="p-4 border border-[#E8E4DC] rounded-lg opacity-80">
                   <h4 className="text-sm font-bold text-[#111111] mb-2">Improve positioning around AI marketing</h4>
                   <div className="flex gap-3 text-[10px] font-bold uppercase tracking-wider">
                      <span className="text-[#800020]">Med Impact</span>
                      <span className="text-[#5A5A5A]">85% Conf</span>
                      <span className="text-[#5A5A5A]">Med Effort</span>
                   </div>
                 </div>
                 <div className="p-4 border border-[#E8E4DC] rounded-lg opacity-60">
                   <h4 className="text-sm font-bold text-[#111111] mb-2">Re-engage inactive audience segment</h4>
                   <div className="flex gap-3 text-[10px] font-bold uppercase tracking-wider">
                      <span className="text-[#5A5A5A]">Low Impact</span>
                      <span className="text-[#5A5A5A]">70% Conf</span>
                      <span className="text-[#5A5A5A]">Low Effort</span>
                   </div>
                 </div>
              </div>
            </div>
            <div className="p-8 pt-0 mt-auto">
               <Link href="#product">
                 <span className="text-[#800020] font-bold text-sm hover:text-[#5C0017]">View All Opportunities &rarr;</span>
               </Link>
            </div>
          </div>
        </ScrollReveal>

      </div>
    </section>
  )
}

export function ExecutionSection() {
  return (
    <section className="py-32 px-6 lg:px-8 bg-transparent border-t border-[#E8E4DC]">
      <div className="max-w-[1400px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16">
        
        {/* Content & Approval */}
        <div className="space-y-12">
          <div className="space-y-4">
            <ScrollReveal delay={0}>
              <h2 className="text-[32px] md:text-[40px] font-bold tracking-tight text-[#111111] leading-[1.1]">
                AI MOVES FAST.<br/>YOU STAY IN CONTROL.
              </h2>
            </ScrollReveal>
            <ScrollReveal delay={0.1}>
              <p className="text-lg text-[#5A5A5A] font-medium">
                From idea to published content, with a clear approval workflow.
              </p>
            </ScrollReveal>
          </div>
          
          <ScrollReveal delay={0.2}>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5A5A5A] flex-wrap">
               <span className="bg-white px-3 py-1.5 rounded border border-[#E8E4DC]">Idea</span>
               <span>&rarr;</span>
               <span className="bg-white px-3 py-1.5 rounded border border-[#E8E4DC]">Brief</span>
               <span>&rarr;</span>
               <span className="bg-white px-3 py-1.5 rounded border border-[#E8E4DC]">Draft</span>
               <span>&rarr;</span>
               <span className="bg-white px-3 py-1.5 rounded border border-[#E8E4DC]">Review</span>
               <span>&rarr;</span>
               <span className="bg-[#111111] text-white px-3 py-1.5 rounded shadow-sm">Approval</span>
               <span>&rarr;</span>
               <span className="bg-white px-3 py-1.5 rounded border border-[#E8E4DC]">Publish</span>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={0.3}>
            <div className="bg-white border border-[#E8E4DC] rounded-[16px] p-6 shadow-xl shadow-[#111111]/5">
              <div className="flex justify-between items-center border-b border-[#E8E4DC] pb-4 mb-4">
                 <div>
                    <div className="text-sm font-bold text-[#111111]">Q4 AI Marketing Guide</div>
                    <div className="text-xs text-[#5A5A5A]">Blog Post</div>
                 </div>
                 <div className="bg-[#F5E6E8] text-[#5C0017] text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded">Awaiting Approval</div>
              </div>
              <div className="space-y-3">
                 <div className="h-2 bg-[#FAF8F3] rounded w-full"></div>
                 <div className="h-2 bg-[#FAF8F3] rounded w-5/6"></div>
                 <div className="h-2 bg-[#FAF8F3] rounded w-4/6"></div>
                 <div className="h-2 bg-[#FAF8F3] rounded w-full"></div>
              </div>
              <div className="mt-6 flex justify-end gap-2">
                 <Button size="sm" variant="outline" className="border-[#E8E4DC] text-[#111111] hover:bg-[#FAF8F3]">Reject</Button>
                 <Button size="sm" className="bg-[#111111] text-white hover:bg-[#171717]">Approve & Publish</Button>
              </div>
            </div>
          </ScrollReveal>
        </div>

        {/* Performance & Learning */}
        <div className="space-y-12">
          <div className="space-y-4">
            <ScrollReveal delay={0}>
              <h2 className="text-[32px] md:text-[40px] font-bold tracking-tight text-[#111111] leading-[1.1]">
                EVERY CAMPAIGN MAKES<br/>THE SYSTEM SMARTER.
              </h2>
            </ScrollReveal>
          </div>
          
          <ScrollReveal delay={0.4} className="h-full">
            <div className="bg-white border border-[#E8E4DC] rounded-[16px] p-8 shadow-xl shadow-[#111111]/5 h-full flex flex-col">
              <div className="text-xs font-bold uppercase tracking-widest text-[#5A5A5A] mb-6">Content Performance</div>
              
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
                 <div>
                    <div className="text-2xl font-bold text-[#111111]">12.4K</div>
                    <div className="text-xs font-semibold text-[#858585]">Impressions</div>
                 </div>
                 <div>
                    <div className="text-2xl font-bold text-[#111111]">8.2%</div>
                    <div className="text-xs font-semibold text-[#858585]">Engagement</div>
                 </div>
                 <div>
                    <div className="text-2xl font-bold text-[#111111]">245</div>
                    <div className="text-xs font-semibold text-[#858585]">Clicks</div>
                 </div>
                 <div>
                    <div className="text-2xl font-bold text-[#168A5B]">12</div>
                    <div className="text-xs font-semibold text-[#858585]">Conversions</div>
                 </div>
              </div>
              
              {/* Mock Chart */}
              <div className="flex-1 min-h-[120px] bg-[#FAF8F3] border border-[#E8E4DC] rounded-xl flex items-end p-4 gap-2 mb-8">
                 <div className="w-1/6 bg-[#800020] rounded-t-sm h-[20%]"></div>
                 <div className="w-1/6 bg-[#800020] rounded-t-sm h-[30%]"></div>
                 <div className="w-1/6 bg-[#800020] rounded-t-sm h-[25%]"></div>
                 <div className="w-1/6 bg-[#800020] rounded-t-sm h-[40%]"></div>
                 <div className="w-1/6 bg-[#800020] rounded-t-sm h-[60%]"></div>
                 <div className="w-1/6 bg-[#800020] rounded-t-sm h-[85%]"></div>
              </div>
              
              <div className="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-[#111111] pt-4 border-t border-[#E8E4DC] flex-wrap gap-2">
                 <span>Measure</span>
                 <span className="text-[#E8E4DC] hidden sm:inline">&bull;</span>
                 <span>Attribute</span>
                 <span className="text-[#E8E4DC] hidden sm:inline">&bull;</span>
                 <span>Learn</span>
                 <span className="text-[#E8E4DC] hidden sm:inline">&bull;</span>
                 <span className="text-[#800020]">Next Best Action</span>
              </div>
            </div>
          </ScrollReveal>
        </div>

      </div>
    </section>
  )
}

