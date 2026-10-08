'use client'

import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { useState } from 'react'
import { 
  Brain, Target, Zap, MessageSquare, Settings, Sparkles, 
  Paperclip, AtSign, Globe, Send, PenTool, FileText, List, ChevronRight, Search, BarChart2
} from 'lucide-react'
import Image from 'next/image'

export function AiCmoSection() {
  const [activeTab, setActiveTab] = useState('Chat')
  const [buttonState, setButtonState] = useState('idle')
  const [inputText, setInputText] = useState('')

  return (
    <section className="py-12 px-6 lg:px-8 bg-[#111111] relative overflow-hidden" id="ai-cmo">
      {/* Abstract Line Art */}
      <div className="absolute inset-0 pointer-events-none opacity-30 flex items-center justify-center">
        <svg width="100%" height="100%" viewBox="0 0 1440 800" fill="none" xmlns="http://www.w3.org/2000/svg">
           <path d="M-100 400C200 400 400 100 720 100C1040 100 1200 700 1540 700" stroke="#800020" strokeWidth="2" strokeOpacity="0.5"/>
           <path d="M-100 450C200 450 400 150 720 150C1040 150 1200 750 1540 750" stroke="#800020" strokeWidth="1" strokeOpacity="0.3"/>
        </svg>
      </div>

      <div className="max-w-[1300px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center relative z-10">
        
        {/* Left Side */}
        <div className="space-y-8">
          <div className="space-y-4">
            <div className="text-[11px] font-bold uppercase tracking-[0.15em] text-[#800020]">
              AI CMO
            </div>
            <h2 className="text-[40px] md:text-[56px] font-extrabold tracking-tight text-white leading-[1.05]">
              Meet your <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF7A85] to-[#B3002D]">AI CMO.</span>
            </h2>
            <p className="text-[22px] md:text-[24px] text-[#F5F3F1] font-bold leading-tight">
              Strategic. Contextual. Actionable.<br/>
              Always on your side.
            </p>
            <p className="text-[#858585] text-base md:text-lg max-w-lg font-medium leading-relaxed">
              Your AI marketing strategist that understands your business, finds opportunities, creates content, and helps you grow — all from one connected brain.
            </p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
             {/* Card 1 */}
             <div className="bg-[#171717] border border-white/5 p-5 rounded-xl space-y-4 hover:border-[#800020]/30 transition-colors cursor-pointer group shadow-sm">
               <div className="w-10 h-10 rounded-lg bg-[#800020]/10 flex items-center justify-center group-hover:bg-[#800020] transition-colors">
                 <Brain className="w-5 h-5 text-[#800020] group-hover:text-white transition-colors" />
               </div>
               <div>
                 <h4 className="text-white font-bold text-sm mb-1">Understands<br/>your business</h4>
                 <p className="text-[#858585] text-xs leading-relaxed">Uses your Brand Brain, data and real-time insights.</p>
               </div>
             </div>
             
             {/* Card 2 */}
             <div className="bg-[#171717] border border-white/5 p-5 rounded-xl space-y-4 hover:border-[#800020]/30 transition-colors cursor-pointer group shadow-sm">
               <div className="w-10 h-10 rounded-lg bg-[#800020]/10 flex items-center justify-center group-hover:bg-[#800020] transition-colors">
                 <Target className="w-5 h-5 text-[#800020] group-hover:text-white transition-colors" />
               </div>
               <div>
                 <h4 className="text-white font-bold text-sm mb-1">Finds<br/>what matters</h4>
                 <p className="text-[#858585] text-xs leading-relaxed">Identifies the highest-value opportunities across channels.</p>
               </div>
             </div>
             
             {/* Card 3 */}
             <div className="bg-[#171717] border border-white/5 p-5 rounded-xl space-y-4 hover:border-[#800020]/30 transition-colors cursor-pointer group shadow-sm">
               <div className="w-10 h-10 rounded-lg bg-[#800020]/10 flex items-center justify-center group-hover:bg-[#800020] transition-colors">
                 <Zap className="w-5 h-5 text-[#800020] group-hover:text-white transition-colors" />
               </div>
               <div>
                 <h4 className="text-white font-bold text-sm mb-1">Coordinates<br/>execution</h4>
                 <p className="text-[#858585] text-xs leading-relaxed">Works with specialized agents to get things done.</p>
               </div>
             </div>
          </div>
          
          <div className="flex flex-col sm:flex-row sm:items-center gap-6 pt-2">
             <Link href="#product">
               <Button size="lg" className="h-[52px] px-6 bg-[#800020] text-white hover:bg-[#6A001A] rounded-xl font-bold border-none flex items-center gap-2 text-base transition-colors shadow-lg shadow-[#800020]/20">
                 <MessageSquare className="w-4 h-4" />
                 Talk to the AI CMO &rarr;
               </Button>
             </Link>
             
             <div className="flex items-center gap-3">
               <div className="flex -space-x-2">
                 <div className="w-8 h-8 rounded-full border-2 border-[#111111] bg-gray-200 overflow-hidden"><img src="https://i.pravatar.cc/100?img=68" alt="Avatar"/></div>
                 <div className="w-8 h-8 rounded-full border-2 border-[#111111] bg-gray-300 overflow-hidden"><img src="https://i.pravatar.cc/100?img=47" alt="Avatar"/></div>
                 <div className="w-8 h-8 rounded-full border-2 border-[#111111] bg-gray-400 overflow-hidden"><img src="https://i.pravatar.cc/100?img=32" alt="Avatar"/></div>
                 <div className="w-8 h-8 rounded-full border-2 border-[#111111] bg-gray-500 overflow-hidden"><img src="https://i.pravatar.cc/100?img=12" alt="Avatar"/></div>
               </div>
               <span className="text-[#858585] text-xs font-medium tracking-wide">Trusted by growing businesses</span>
             </div>
          </div>
        </div>
        
        {/* Right Side - Chat Mockup */}
        <div className="w-full relative max-w-[650px] mx-auto lg:mx-0">
          <div className="bg-[#1A1A1A] rounded-2xl border border-white/5 shadow-2xl overflow-hidden flex flex-col h-[540px] relative z-20">
             
             {/* Header */}
             <div className="h-[64px] border-b border-white/5 flex items-center justify-between px-5 shrink-0">
                <div className="flex items-center gap-3.5">
                  <div className="w-11 h-11 rounded-lg bg-[#800020] flex items-center justify-center shrink-0">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-base leading-tight">AI CMO</h3>
                    <p className="text-[#858585] text-xs font-medium">Your always-on marketing strategist</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="bg-[#111111] border border-white/5 rounded-full px-3 py-1.5 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#168A5B]"></div>
                    <span className="text-[#F5F3F1] text-xs font-semibold">Online</span>
                  </div>
                  <button className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-white/5 text-[#858585] hover:text-white transition-colors border border-white/5">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
             </div>
             
             {/* Tabs */}
             <div className="flex px-4 border-b border-white/5 shrink-0">
                {['Chat', 'Research', 'Strategy', 'Tasks'].map((tab) => (
                  <button 
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-5 py-4 text-sm font-semibold border-b-2 transition-colors ${activeTab === tab ? 'text-white border-[#800020]' : 'text-[#858585] border-transparent hover:text-white'}`}
                  >
                    {tab}
                  </button>
                ))}
             </div>
             
             {/* Chat Body */}
             <div className="flex-1 p-5 overflow-y-auto flex flex-col gap-4 bg-[#171717] [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-white/10 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-white/20 relative">
                {activeTab === 'Chat' && (
                  <div className="flex flex-col gap-4 animate-in fade-in zoom-in-95 duration-200">
                    {/* User Message */}
                    <div className="flex flex-col items-end w-full">
                   <div className="flex items-start gap-3 flex-row-reverse max-w-[85%]">
                     <div className="w-8 h-8 rounded-full bg-[#5143E5] flex items-center justify-center text-white text-sm font-bold shrink-0 shadow-sm">
                       A
                     </div>
                     <div className="bg-[#800020] text-white px-4 py-3.5 rounded-2xl rounded-tr-sm text-sm shadow-sm font-medium">
                       What should we focus on this week?
                     </div>
                   </div>
                </div>
                
                {/* AI Response */}
                <div className="flex flex-col items-start w-full">
                   <div className="flex items-start gap-3 w-full">
                     <div className="w-8 h-8 rounded-lg bg-[#800020] flex items-center justify-center shrink-0 shadow-sm">
                       <Sparkles className="w-4 h-4 text-white" />
                     </div>
                     <div className="bg-[#222222] border border-white/5 p-5 rounded-2xl rounded-tl-sm w-full shadow-sm">
                       <p className="text-[#F5F3F1] text-sm mb-3 font-medium leading-relaxed">
                         Based on your brand, audience and recent performance, I've identified 3 high-impact opportunities.
                       </p>
                       
                       {/* Opportunity List */}
                       <div className="space-y-2 mb-3">
                          {/* Item 1 */}
                          <div className="bg-[#171717] border border-white/5 p-4 rounded-xl flex items-center justify-between group cursor-pointer hover:border-white/20 transition-all hover:bg-[#1A1A1A]">
                             <div className="flex items-center gap-4">
                               <div className="w-7 h-7 rounded-full bg-[#800020] text-white flex items-center justify-center text-xs font-bold shrink-0">1</div>
                               <div>
                                 <h5 className="text-white text-sm font-semibold mb-1 group-hover:text-[#FF7A85] transition-colors leading-tight">Improve positioning around AI-powered marketing systems</h5>
                                 <p className="text-[#858585] text-xs font-medium">Target high-intent keywords and refine messaging.</p>
                               </div>
                             </div>
                             <div className="flex items-center gap-3 shrink-0 ml-4">
                               <span className="text-[10px] uppercase font-bold text-[#858585] bg-[#222222] px-2 py-1 rounded">SEO</span>
                               <ChevronRight className="w-4 h-4 text-[#555] group-hover:text-white transition-colors" />
                             </div>
                          </div>
                          
                          {/* Item 2 */}
                          <div className="bg-[#171717] border border-white/5 p-4 rounded-xl flex items-center justify-between group cursor-pointer hover:border-white/20 transition-all hover:bg-[#1A1A1A]">
                             <div className="flex items-center gap-4">
                               <div className="w-7 h-7 rounded-full bg-[#800020] text-white flex items-center justify-center text-xs font-bold shrink-0">2</div>
                               <div>
                                 <h5 className="text-white text-sm font-semibold mb-1 group-hover:text-[#FF7A85] transition-colors leading-tight">Launch a thought-leadership content series</h5>
                                 <p className="text-[#858585] text-xs font-medium">Establish authority and drive organic growth.</p>
                               </div>
                             </div>
                             <div className="flex items-center gap-3 shrink-0 ml-4">
                               <span className="text-[10px] uppercase font-bold text-[#858585] bg-[#222222] px-2 py-1 rounded">Content</span>
                               <ChevronRight className="w-4 h-4 text-[#555] group-hover:text-white transition-colors" />
                             </div>
                          </div>
                          
                          {/* Item 3 */}
                          <div className="bg-[#171717] border border-white/5 p-4 rounded-xl flex items-center justify-between group cursor-pointer hover:border-white/20 transition-all hover:bg-[#1A1A1A]">
                             <div className="flex items-center gap-4">
                               <div className="w-7 h-7 rounded-full bg-[#800020] text-white flex items-center justify-center text-xs font-bold shrink-0">3</div>
                               <div>
                                 <h5 className="text-white text-sm font-semibold mb-1 group-hover:text-[#FF7A85] transition-colors leading-tight">Re-engage inactive audience segment</h5>
                                 <p className="text-[#858585] text-xs font-medium">Create a targeted campaign to bring them back.</p>
                               </div>
                             </div>
                             <div className="flex items-center gap-3 shrink-0 ml-4">
                               <span className="text-[10px] uppercase font-bold text-[#858585] bg-[#222222] px-2 py-1 rounded">Growth</span>
                               <ChevronRight className="w-4 h-4 text-[#555] group-hover:text-white transition-colors" />
                             </div>
                          </div>
                       </div>
                       
                       {/* Action Buttons */}
                       <div className="flex flex-wrap gap-2.5">
                         <button 
                           onClick={() => setButtonState(prev => prev === 'creating' ? 'idle' : 'creating')}
                           className="px-4 py-2.5 bg-white text-[#111111] text-xs font-bold rounded-lg hover:bg-[#F5F3F1] flex items-center gap-2 transition-all shadow-sm"
                         >
                           <PenTool className="w-3.5 h-3.5" />
                           {buttonState === 'creating' ? 'Creating...' : 'Create Strategy'}
                         </button>
                         <button className="px-4 py-2.5 bg-transparent border border-white/10 text-white text-xs font-semibold rounded-lg hover:bg-white/5 flex items-center gap-2 transition-all">
                           <FileText className="w-3.5 h-3.5 text-[#858585]" />
                           Create Content
                         </button>
                         <button className="px-4 py-2.5 bg-transparent border border-white/10 text-white text-xs font-semibold rounded-lg hover:bg-white/5 flex items-center gap-2 transition-all">
                           <List className="w-3.5 h-3.5 text-[#858585]" />
                           View Opportunities
                         </button>
                       </div>
                       
                     </div>
                   </div>
                </div>
                </div>
                )}

                {activeTab === 'Research' && (
                  <div className="flex flex-col gap-4 w-full animate-in fade-in zoom-in-95 duration-200">
                    <div className="bg-[#222222] border border-white/5 p-4 rounded-xl shadow-sm">
                      <div className="flex items-center gap-2 mb-4">
                        <div className="w-8 h-8 rounded-lg bg-[#800020]/20 flex items-center justify-center">
                          <Search className="w-4 h-4 text-[#FF7A85]" />
                        </div>
                        <h4 className="text-white text-sm font-bold">Latest Market Insights</h4>
                      </div>
                      <div className="space-y-3">
                        <div className="bg-[#1A1A1A] p-4 rounded-lg border border-white/5 hover:border-white/20 transition-colors cursor-pointer group">
                          <div className="flex justify-between items-start mb-2">
                            <h5 className="text-[#F5F3F1] text-sm font-semibold group-hover:text-[#FF7A85] transition-colors">Competitor X launched new feature</h5>
                            <span className="text-[10px] uppercase font-bold text-[#858585] bg-[#222222] px-2 py-1 rounded">2h ago</span>
                          </div>
                          <p className="text-[#858585] text-xs">They are aggressively targeting the SMB segment with a 20% discount campaign. We should highlight our ROI.</p>
                        </div>
                        <div className="bg-[#1A1A1A] p-4 rounded-lg border border-white/5 hover:border-white/20 transition-colors cursor-pointer group">
                          <div className="flex justify-between items-start mb-2">
                            <h5 className="text-[#F5F3F1] text-sm font-semibold group-hover:text-[#FF7A85] transition-colors">Trending Keyword: "AI Marketing"</h5>
                            <span className="text-[10px] uppercase font-bold text-[#858585] bg-[#222222] px-2 py-1 rounded">Trending</span>
                          </div>
                          <p className="text-[#858585] text-xs">Search volume increased by 45% this week. Low keyword difficulty. Opportunity to capture early traffic.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {activeTab === 'Strategy' && (
                  <div className="flex flex-col gap-4 w-full animate-in fade-in zoom-in-95 duration-200">
                    <div className="bg-[#222222] border border-white/5 p-4 rounded-xl shadow-sm">
                      <div className="flex items-center gap-2 mb-4">
                        <div className="w-8 h-8 rounded-lg bg-[#800020]/20 flex items-center justify-center">
                          <Target className="w-4 h-4 text-[#FF7A85]" />
                        </div>
                        <h4 className="text-white text-sm font-bold">Q4 Growth Strategy</h4>
                      </div>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between bg-[#1A1A1A] p-4 rounded-lg border border-white/5 group hover:border-white/20 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-[#168A5B]/20 flex items-center justify-center shrink-0">
                              <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                            </div>
                            <div>
                              <h5 className="text-[#F5F3F1] text-sm font-semibold group-hover:text-white transition-colors">SEO Domination Play</h5>
                              <p className="text-[#858585] text-xs mt-0.5">Publish 10 pillar pages on AI Marketing.</p>
                            </div>
                          </div>
                          <span className="px-2 py-1 bg-[#168A5B]/20 text-[#168A5B] rounded text-[10px] font-bold">ACTIVE</span>
                        </div>
                        <div className="flex items-center justify-between bg-[#1A1A1A] p-4 rounded-lg border border-white/5 group hover:border-white/20 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-[#333] flex items-center justify-center shrink-0">
                              <span className="w-2 h-2 rounded-full bg-[#858585]"></span>
                            </div>
                            <div>
                              <h5 className="text-[#F5F3F1] text-sm font-semibold group-hover:text-white transition-colors">LinkedIn Social Selling</h5>
                              <p className="text-[#858585] text-xs mt-0.5">Automated thought leadership posts 3x/week.</p>
                            </div>
                          </div>
                          <span className="px-2 py-1 bg-[#222222] text-[#858585] rounded text-[10px] font-bold border border-white/10">DRAFT</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {activeTab === 'Tasks' && (
                  <div className="flex flex-col gap-4 w-full animate-in fade-in zoom-in-95 duration-200">
                    <div className="bg-[#222222] border border-white/5 p-4 rounded-xl shadow-sm">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-lg bg-[#800020]/20 flex items-center justify-center">
                            <List className="w-4 h-4 text-[#FF7A85]" />
                          </div>
                          <h4 className="text-white text-sm font-bold">Active Agent Tasks</h4>
                        </div>
                        <span className="text-[10px] bg-[#168A5B]/20 text-[#168A5B] font-bold px-2 py-0.5 rounded-full">2 Running</span>
                      </div>
                      <div className="space-y-3">
                        <div className="bg-[#1A1A1A] p-4 rounded-lg border border-white/5">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 rounded bg-white/5 flex items-center justify-center">
                              <PenTool className="w-3 h-3 text-[#FBBC04]" />
                            </div>
                            <h5 className="text-[#F5F3F1] text-xs font-bold uppercase tracking-wider">Writer Agent</h5>
                          </div>
                          <p className="text-white text-sm font-medium mb-3">Drafting "How to automate marketing" blog post.</p>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 bg-[#333] h-1.5 rounded-full overflow-hidden">
                              <div className="bg-[#800020] w-[65%] h-full rounded-full relative overflow-hidden">
                                <div className="absolute inset-0 bg-white/20 w-full animate-[shimmer_2s_infinite]"></div>
                              </div>
                            </div>
                            <span className="text-[#858585] text-[10px] font-bold">65%</span>
                          </div>
                        </div>
                        <div className="bg-[#1A1A1A] p-4 rounded-lg border border-white/5">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 rounded bg-white/5 flex items-center justify-center">
                              <BarChart2 className="w-3 h-3 text-[#4285F4]" />
                            </div>
                            <h5 className="text-[#F5F3F1] text-xs font-bold uppercase tracking-wider">Analytics Agent</h5>
                          </div>
                          <p className="text-white text-sm font-medium mb-3">Compiling weekly traffic and conversion report.</p>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 bg-[#333] h-1.5 rounded-full overflow-hidden">
                              <div className="bg-[#168A5B] w-[90%] h-full rounded-full relative overflow-hidden">
                                <div className="absolute inset-0 bg-white/20 w-full animate-[shimmer_2s_infinite]"></div>
                              </div>
                            </div>
                            <span className="text-[#858585] text-[10px] font-bold">90%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
             </div>
             
             {/* Input Area */}
             <div className="p-4 bg-[#1A1A1A] border-t border-white/5 shrink-0">
               <div className="bg-[#222222] border border-white/10 rounded-xl pl-4 pr-1.5 py-1.5 flex items-center gap-3 focus-within:border-[#800020] transition-colors group">
                  <input 
                    type="text" 
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Ask the AI CMO anything..." 
                    className="bg-transparent border-none outline-none text-sm font-medium text-white w-full placeholder-[#666]"
                  />
                  <div className="flex items-center gap-1.5 text-[#666] shrink-0">
                     <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/5 hover:text-white transition-colors"><Paperclip className="w-4 h-4" /></button>
                     <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/5 hover:text-white transition-colors"><AtSign className="w-4 h-4" /></button>
                     <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/5 hover:text-white transition-colors"><Globe className="w-4 h-4" /></button>
                     <button 
                       className={`w-9 h-9 ml-1 flex items-center justify-center rounded-lg transition-colors shadow-sm ${inputText.length > 0 ? 'bg-[#800020] text-white hover:bg-[#6A001A]' : 'bg-[#800020] text-white opacity-80'}`}
                       onClick={() => setInputText('')}
                     >
                       <Send className="w-4 h-4" />
                     </button>
                  </div>
               </div>
             </div>
             
          </div>
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
        <div>
          <div className="flex flex-col h-full bg-[#FAF8F3] border border-[#E8E4DC] rounded-[24px] overflow-hidden">
            <div className="p-8 pb-4">
              <h3 className="text-2xl font-bold text-[#111111] mb-2">Brand Brain</h3>
              <p className="text-[#5A5A5A] text-sm font-medium">Your company&apos;s intelligence foundation.</p>
            </div>
            <div className="flex-1 px-8 pb-8 pt-4">
              <div className="bg-white border border-[#E8E4DC] rounded-xl p-4 shadow-sm h-full space-y-3">
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Website Analysis</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Audience</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Brand Voice</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Product and Services</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">All Documents</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Product Information</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm border-b border-[#E8E4DC] pb-2">
                    <span className="font-semibold text-[#111111]">Marketing Strategy</span>
                    <span className="w-2 h-2 rounded-full bg-[#168A5B]"></span>
                 </div>
                 <div className="flex justify-between items-center text-sm">
                    <span className="font-semibold text-[#111111]">Brand Voice Guide</span>
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
        </div>

        {/* Specialized Agents */}
        <div>
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
        </div>
        
        {/* Opportunities */}
        <div>
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
        </div>

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
            <div>
              <h2 className="text-[32px] md:text-[40px] font-bold tracking-tight text-[#111111] leading-[1.1]">
                AI MOVES FAST.<br/>YOU STAY IN CONTROL.
              </h2>
            </div>
            <div>
              <p className="text-lg text-[#5A5A5A] font-medium">
                From idea to published content, with a clear approval workflow.
              </p>
            </div>
          </div>
          
          <div>
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
          </div>

          <div>
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
          </div>
        </div>

        {/* Performance & Learning */}
        <div className="space-y-12">
          <div className="space-y-4">
            <div>
              <h2 className="text-[32px] md:text-[40px] font-bold tracking-tight text-[#111111] leading-[1.1]">
                EVERY CAMPAIGN MAKES<br/>THE SYSTEM SMARTER.
              </h2>
            </div>
          </div>
          
          <div>
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
          </div>
        </div>

      </div>
    </section>
  )
}

