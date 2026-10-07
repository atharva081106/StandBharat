'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'

const AGENTS = [
  { name: 'Growth Agent', desc: 'Find high-impact opportunities.', iconPath: 'M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941' },
  { name: 'SEO Agent', desc: 'Find gaps, draft pages.', iconPath: 'M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 15.803a7.5 7.5 0 0010.607 10.607z' },
  { name: 'Content Writer Agent', desc: 'Draft in your brand voice.', iconPath: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z' },
  { name: 'Analytics Agent', desc: "Surface what's working.", iconPath: 'M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z' },
  { name: 'Competitor Agent', desc: 'Monitor and exploit gaps.', iconPath: 'M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178zM15 12a3 3 0 11-6 0 3 3 0 016 0z' },
  { name: 'Content Strategy Agent', desc: 'Build data-driven briefs.', iconPath: 'M6.75 7.5l3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0021 18V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v12a2.25 2.25 0 002.25 2.25z' },
  { name: 'Audience Agent', desc: "Understand who's listening.", iconPath: 'M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z' },
  { name: 'Brand Voice Agent', desc: 'Keep every word on-brand.', iconPath: 'M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z' },
]

const INTEGRATIONS = [
  { name: 'WordPress', desc: 'Auto-publish posts.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#21759b" className="w-5 h-5"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-.91 14.51L8.52 10.3l-2.45 6.64A8.046 8.046 0 014 12c0-1.8.61-3.46 1.63-4.78.21.03.44.05.67.05 1.05 0 2.66-.13 2.66-.13.56-.03.64.79.08.84 0 0-.54.06-1.15.1l3.59 10.73 2.16-6.49-3.08-8.61c-.57-.04-1.12-.1-1.12-.1-.56-.03-.48-.87.08-.84 0 0 1.63.13 2.62.13.96 0 2.61-.13 2.61-.13.56-.03.64.79.08.84 0 0-.55.06-1.15.1L16.27 15l-1.99 5.86c-.16-.07-.32-.15-.47-.24-.26-.14-.52-.3-.77-.48l-1.95-3.63zm7.04-4.88c0 1.25-.45 2.21-.86 3.14l-2.61 7.6c1.94-1.29 3.23-3.48 3.23-6.02 0-1.74-.63-3.05-1.42-4.14-.14-.18-.3-.36-.45-.54-.01-.01-.02-.02-.02-.04H16.4l1.73 4z" /></svg> },
  { name: 'Webflow', desc: 'Publish to Webflow.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#4353FF" className="w-5 h-5"><path d="M16.89 6.27h-4.3l-1.57 6.42-2.18-6.42h-4.3l3.88 11.46h4.52l1.9-7.3 1.9 7.3h4.52L25.13 6.27h-4.18l-1.9 8.16-2.16-8.16z" transform="translate(-1.4, 0) scale(0.9)"/></svg> },
  { name: 'Framer', desc: 'Sync Framer content.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#000000" className="w-5 h-5"><path d="M4 2h16v7H12L4 2zm16 7v7H4l8-7h8zm-8 7v7l-8-7h8z"/></svg> },

  { name: 'Wix', desc: 'Publish to Wix blog.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#000000" className="w-5 h-5"><path d="M12.98 17.5l-2.58-8.23-2.58 8.23H5.5L2 6.5h2.51l2.13 7.23 2.5-7.23h2.38l2.5 7.23 2.13-7.23H22l-3.5 11h-2.32V17.5h-3.2z"/></svg> },
  { name: 'Sanity', desc: 'Publish content.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#F03E2F" className="w-5 h-5"><path d="M16.71 5.37l-4.5 5.56 1.83 4.19 5.36-6.4-2.69-3.35zM4.6 7.49L2.6 10l5.88 7.02 2.69-3.35-6.57-6.18zM14.6 18.63l-2.69 3.35L7.4 16.41l2.69-3.35 4.51 5.57z"/></svg> },
  { name: 'Google Search Console', desc: 'Track rankings.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#4285F4" className="w-5 h-5"><path d="M3 19h18v2H3v-2zm10-5h4v4h-4v-4zm-5-3h4v7H8v-7zm-5-4h4v11H3V7zm15-4h4v15h-4V3z"/></svg> },

  { name: 'Google Analytics', desc: 'Track traffic.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#F9AB00" className="w-5 h-5"><path d="M16 3h4v18h-4V3zm-6 7h4v11h-4V10zM4 14h4v7H4v-7z"/></svg> },
  { name: 'GitHub', desc: 'Open SEO PRs.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#181717" className="w-5 h-5"><path d="M12 .3a12 12 0 00-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.5-1.4-1.3-1.8-1.3-1.8-1-1 .1-1 .1-1 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.8-1.6-2.7-.3-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 016 0c2.3-1.5 3.3-1.2 3.3-1.2.6 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0012 .3z"/></svg> },
  { name: 'LinkedIn', desc: 'Publish posts.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#0A66C2" className="w-5 h-5"><path d="M20.4 20.5H16.9v-5.6c0-1.3-.5-2.2-1.6-2.2-1 0-1.5.6-1.8 1.2-.1.2-.1.5-.1.8v5.8H9.9s.1-10.5 0-11.6h3.5v1.6c.5-.7 1.3-1.8 3.2-1.8 2.3 0 4 1.5 4 4.8v7zM5 7.4a2 2 0 110-4.1 2 2 0 010 4.1zm1.8 13.1H3.3V8.9h3.5v11.6z"/></svg> },

  { name: 'X (Twitter)', desc: 'Publish threads.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#000000" className="w-5 h-5"><path d="M18.9 3h3.4l-7.4 8.5 8.7 11.5h-6.8l-5.3-7-6.1 7H2.1l7.9-9L1.8 3h7l4.8 6.3L18.9 3zM15.4 20.8h1.9L6.5 4.9H4.4l11 15.9z"/></svg> },
  { name: 'WhatsApp', desc: 'Drafts in chat.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#25D366" className="w-5 h-5"><path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38c1.45.83 3.1 1.27 4.79 1.27 5.46 0 9.91-4.45 9.91-9.91S17.5 2 12.04 2zm5.46 14.1c-.2.58-1.15 1.11-1.74 1.23-.55.12-1.28.25-3.86-.82-3.13-1.3-5.18-4.52-5.34-4.73-.15-.22-1.27-1.7-1.27-3.24 0-1.55.81-2.32 1.1-2.62.28-.3.62-.38.83-.38.2 0 .4 0 .58.01.2.01.46-.08.72.54.27.65.92 2.24 1 2.44.08.2.14.43.01.68-.13.25-.2.41-.4.65-.2.23-.42.52-.6.7-.2.22-.42.45-.18.86.23.4 1.03 1.7 2.21 2.75 1.52 1.35 2.8 1.77 3.2 1.96.4.2.64.16.88-.1.25-.27 1.03-1.2 1.3-1.61.28-.41.56-.34.92-.2l2.3 1.09c.35.17.58.26.66.4.08.14.08.82-.12 1.4z"/></svg> },
  { name: 'Telegram', desc: 'Updates in chat.', soon: false, icon: <svg viewBox="0 0 24 24" fill="#26A5E4" className="w-5 h-5"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.06-.19-.07-.05-.17-.03-.25-.01-.11.02-1.89 1.18-5.35 3.51-.51.35-.97.53-1.38.52-.45-.01-1.32-.26-1.96-.46-.79-.26-1.42-.39-1.37-.83.02-.23.32-.47.9-.72 3.53-1.53 5.88-2.54 7.05-3.03 3.35-1.4 4.04-1.64 4.49-1.65.1 0 .32.02.46.12.12.09.16.21.17.33 0 .07-.01.21-.02.32z"/></svg> },

  { name: 'TikTok', desc: 'Publish clips.', soon: true, icon: <svg viewBox="0 0 24 24" fill="#000000" className="w-5 h-5"><path d="M12.53.02C13.84 0 15.14.01 16.44 0c.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 2.78-1.15 5.54-3.11 7.42-2.12 2.05-5.07 3.03-7.98 2.68-2.9-.34-5.46-1.89-7.14-4.23-1.64-2.26-2.14-5.2-1.33-7.85.79-2.67 2.69-4.87 5.17-5.96 1.48-.65 3.12-.91 4.72-.77v4.11c-1.59-.14-3.23.47-4.27 1.64-1.04 1.15-1.4 2.82-1.01 4.3.4 1.5 1.54 2.7 2.96 3.25 1.42.54 3.06.41 4.37-.36 1.33-.78 2.21-2.16 2.42-3.69.08-.57.1-1.15.1-1.72V.02h-1.04z"/></svg> },
  { name: 'Instagram', desc: 'Publish clips.', soon: true, icon: <svg viewBox="0 0 24 24" fill="#E4405F" className="w-5 h-5"><path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.22.41.56.22.96.48 1.36.88.4.4.66.8.88 1.36.16.42.36 1.05.41 2.22.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.22-.22.56-.48.96-.88 1.36-.4.4-.8.66-1.36.88-.42.16-1.05.36-2.22.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.22-.41-.56-.22-.96-.48-1.36-.88-.4-.4-.66-.8-.88-1.36-.16-.42-.36-1.05-.41-2.22C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.22.22-.56.48-.96.88-1.36.4-.4.8-.66 1.36-.88.42-.16 1.05-.36 2.22-.41C8.42 2.17 8.8 2.16 12 2.16M12 0C8.74 0 8.33.01 7.05.07c-1.27.06-2.14.26-2.9.56-.78.3-1.44.73-2.1 1.39-.66.66-1.09 1.32-1.39 2.1-.3.76-.5 1.63-.56 2.9C.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.14.56 2.9.3.78.73 1.44 1.39 2.1.66.66 1.32 1.09 2.1 1.39.76.3 1.63.5 2.9.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.14-.26 2.9-.56.78-.3 1.44-.73 2.1-1.39.66-.66 1.09-1.32 1.39-2.1.3-.76.5-1.63.56-2.9.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.14-.56-2.9-.3-.78-.73-1.44-1.39-2.1-.66-.66-1.32-1.09-2.1-1.39-.76-.3-1.63-.5-2.9-.56C15.67.01 15.26 0 12 0zm0 5.84A6.16 6.16 0 1018.16 12 6.16 6.16 0 0012 5.84zm0 10.16A4 4 0 1116 12a4 4 0 01-4 4zm5.22-9.62a1.44 1.44 0 11-2.88 0 1.44 1.44 0 012.88 0z"/></svg> },
  { name: 'Slack', desc: 'Drafts and approvals.', soon: true, icon: <svg viewBox="0 0 24 24" fill="#4A154B" className="w-5 h-5"><path d="M5.04 15.27a2.38 2.38 0 01-2.38 2.38 2.38 2.38 0 01-2.38-2.38c0-1.3.99-2.37 2.27-2.38h2.49v2.38zm1.19-2.38a2.38 2.38 0 012.38-2.38 2.38 2.38 0 012.38 2.38v5.94a2.38 2.38 0 11-4.76 0v-5.94zM8.73 5.04A2.38 2.38 0 016.35 2.66 2.38 2.38 0 018.73.28c1.3 0 2.37.99 2.38 2.27v2.49H8.73zm2.38 1.19a2.38 2.38 0 012.38 2.38 2.38 2.38 0 01-2.38 2.38H5.17a2.38 2.38 0 110-4.76h5.94zm7.85 2.5a2.38 2.38 0 012.38-2.38 2.38 2.38 0 012.38 2.38c0 1.3-.99 2.37-2.27 2.38h-2.49V8.73zm-1.19 2.38a2.38 2.38 0 01-2.38 2.38 2.38 2.38 0 01-2.38-2.38V5.17a2.38 2.38 0 114.76 0v5.94zM15.27 18.96a2.38 2.38 0 012.38 2.38 2.38 2.38 0 01-2.38 2.38c-1.3 0-2.37-.99-2.38-2.27v-2.49h2.38zm-2.38-1.19a2.38 2.38 0 01-2.38-2.38 2.38 2.38 0 012.38-2.38h5.94a2.38 2.38 0 110 4.76h-5.94z"/></svg> },
]

function AgentIcon({ path }: { path: string }) {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d={path} />
    </svg>
  )
}

function AgentsDropdown() {
  return (
    <div className="absolute top-full left-1/2 -translate-x-1/2 pt-3 w-[860px] z-50">
      <div className="absolute top-[6px] left-1/2 -translate-x-1/2 w-3 h-3 bg-white border-l border-t border-[#E8E4DC] rotate-45 z-10" />
      <div className="bg-white border border-[#E8E4DC] rounded-2xl shadow-2xl shadow-black/10 overflow-hidden flex">
        <div className="flex-1 p-4 grid grid-cols-2 gap-0.5">
          {AGENTS.map((agent, i) => (
            <Link
              key={i}
              href="#product"
              className="flex items-start gap-3 p-3.5 rounded-xl hover:bg-[#FAF8F3] group transition-colors duration-150"
            >
              <div className="mt-0.5 w-9 h-9 rounded-xl bg-[#F5E6E8] text-[#800020] flex items-center justify-center shrink-0 group-hover:bg-[#800020] group-hover:text-white transition-all duration-150">
                <AgentIcon path={agent.iconPath} />
              </div>
              <div>
                <div className="text-sm font-bold text-[#111111] group-hover:text-[#800020] transition-colors duration-150 leading-tight">
                  {agent.name}
                </div>
                <div className="text-[11px] text-[#858585] font-medium mt-0.5 leading-snug">{agent.desc}</div>
              </div>
            </Link>
          ))}
        </div>
        <div className="w-[230px] bg-[#111111] p-6 flex flex-col justify-between shrink-0">
          <div>
            <div className="w-8 h-8 rounded-xl bg-[#800020] flex items-center justify-center mb-4">
              <div className="w-3 h-3 rounded-full bg-white" />
            </div>
            <p className="text-white text-sm font-semibold leading-relaxed">
              &ldquo;StandBharat&apos;s agents found 3 growth opportunities in the first week &mdash; automatically.&rdquo;
            </p>
          </div>
          <div className="pt-5 border-t border-white/10 mt-6">
            <div className="text-[#858585] text-[10px] font-bold uppercase tracking-widest mb-3">Orchestrated by</div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-5 h-5 rounded-md bg-[#800020] flex items-center justify-center">
                <div className="w-1.5 h-1.5 rounded-full bg-white" />
              </div>
              <span className="text-white text-xs font-bold">StandBharat AI CMO</span>
            </div>
            <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-signup')) }}>
              <span className="text-[#800020] text-xs font-bold hover:text-[#F5E6E8] transition-colors">
                Explore all agents &rarr;
              </span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

function IntegrationsDropdown() {
  return (
    <div className="absolute top-full left-1/2 -translate-x-1/2 pt-3 w-[1000px] z-50">
      <div className="absolute top-[6px] left-1/2 -translate-x-1/2 w-3 h-3 bg-white border-l border-t border-[#E8E4DC] rotate-45 z-10" />
      <div className="bg-white border border-[#E8E4DC] rounded-2xl shadow-2xl shadow-black/10 overflow-hidden flex">
        <div className="flex-1 p-4 grid grid-cols-3 gap-0.5">
          {INTEGRATIONS.map((integration, i) => (
            <Link
              key={i}
              href="#integrations"
              className="flex items-start gap-3 p-3 rounded-xl hover:bg-[#FAF8F3] group transition-colors duration-150"
            >
              <div className="mt-0.5 w-10 h-10 rounded-xl bg-white shadow-sm border border-[#E8E4DC] flex items-center justify-center shrink-0 group-hover:border-[#800020] transition-colors duration-150 p-2">
                {integration.icon}
              </div>
              <div>
                <div className="text-sm font-bold text-[#111111] group-hover:text-[#800020] transition-colors duration-150 leading-tight flex items-center gap-1.5">
                  {integration.name}
                  {integration.soon && (
                    <span className="text-[8px] font-bold uppercase tracking-wider border border-[#E8E4DC] bg-white text-[#5A5A5A] px-1.5 py-0.5 rounded-sm">Soon</span>
                  )}
                </div>
                <div className="text-[11px] text-[#858585] font-medium mt-0.5 leading-snug">{integration.desc}</div>
              </div>
            </Link>
          ))}
        </div>
        <div className="w-[260px] bg-[#111111] p-6 flex flex-col justify-between shrink-0">
          <div>
            <div className="w-8 h-8 rounded-xl bg-[#800020] flex items-center justify-center mb-4">
              <div className="w-3 h-3 rounded-full bg-white" />
            </div>
            <p className="text-white text-[15px] font-medium leading-relaxed">
              &ldquo;StandBharat has transformed how we market Quest Dating. It gives us the clarity, consistency, and momentum we need to scale with confidence.&rdquo;
            </p>
          </div>
          <div className="pt-5 border-t border-white/10 mt-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[#800020] flex items-center justify-center text-white text-xs font-bold shrink-0">
                BP
              </div>
              <div>
                <div className="text-white text-xs font-bold">Brian Proctor</div>
                <div className="text-[#858585] text-[11px] font-medium mt-0.5">Solo founder &middot; Quest Dating</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export function MarketingNavbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [agentsOpen, setAgentsOpen] = useState(false)
  const [integrationsOpen, setIntegrationsOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 bg-[#FAF8F3]/90 backdrop-blur-md border-b border-[#E8E4DC]">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/landingpage" className="flex items-center gap-2 shrink-0">
          <div className="w-6 h-6 rounded-md bg-[#800020] flex items-center justify-center">
            <div className="w-2 h-2 rounded-full bg-white" />
          </div>
          <span className="font-bold text-lg tracking-tight text-[#111111]">StandBharat</span>
        </Link>

        <nav className="hidden lg:flex items-center gap-8">
          <Link href="#product" className="text-sm font-semibold text-[#5A5A5A] hover:text-[#800020] transition-colors">Product</Link>
          <Link href="#ai-cmo" className="text-sm font-semibold text-[#5A5A5A] hover:text-[#800020] transition-colors">AI CMO</Link>

          <div
            className="relative"
            onMouseEnter={() => setAgentsOpen(true)}
            onMouseLeave={() => setAgentsOpen(false)}
          >
            <button
              className={`flex items-center gap-1 text-sm font-semibold transition-colors select-none ${agentsOpen ? 'text-[#800020]' : 'text-[#5A5A5A] hover:text-[#800020]'}`}
            >
              Agents
              <svg
                className={`w-3.5 h-3.5 transition-transform duration-200 ${agentsOpen ? 'rotate-180' : ''}`}
                fill="none" viewBox="0 0 24 24" strokeWidth="2.5" stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
              </svg>
            </button>
            <div className={`transition-all duration-200 ${agentsOpen ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 -translate-y-2 pointer-events-none'}`}>
              <AgentsDropdown />
            </div>
          </div>

          <div
            className="relative"
            onMouseEnter={() => setIntegrationsOpen(true)}
            onMouseLeave={() => setIntegrationsOpen(false)}
          >
            <button
              className={`flex items-center gap-1 text-sm font-semibold transition-colors select-none ${integrationsOpen ? 'text-[#800020]' : 'text-[#5A5A5A] hover:text-[#800020]'}`}
            >
              Integrations
              <svg
                className={`w-3.5 h-3.5 transition-transform duration-200 ${integrationsOpen ? 'rotate-180' : ''}`}
                fill="none" viewBox="0 0 24 24" strokeWidth="2.5" stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
              </svg>
            </button>
            <div className={`transition-all duration-200 ${integrationsOpen ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 -translate-y-2 pointer-events-none'}`}>
              <IntegrationsDropdown />
            </div>
          </div>

          <Link href="#solutions" className="text-sm font-semibold text-[#5A5A5A] hover:text-[#800020] transition-colors">Solutions</Link>
          <Link href="/#pricing" className="text-sm font-semibold text-[#5A5A5A] hover:text-[#800020] transition-colors">Pricing</Link>
        </nav>

        <div className="hidden lg:flex items-center gap-4 shrink-0">
          <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-login')) }} className="text-sm font-semibold text-[#111111] hover:text-[#800020] transition-colors">Log in</Link>
          <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-signup')) }}>
            <Button className="bg-[#800020] text-white hover:bg-[#5C0017] font-bold rounded-lg px-5 h-10 border-none shadow-sm shadow-[#800020]/20">
              Get Started
            </Button>
          </Link>
        </div>

        <div className="lg:hidden">
          <button type="button" className="text-[#111111] p-2" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            <span className="sr-only">Open main menu</span>
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="lg:hidden absolute top-16 left-0 right-0 bg-white border-b border-[#E8E4DC] p-6 shadow-xl flex flex-col gap-6 z-40 max-h-[85vh] overflow-y-auto">
          <nav className="flex flex-col gap-4">
            <Link href="#product" className="text-base font-bold text-[#111111]" onClick={() => setMobileMenuOpen(false)}>Product</Link>
            <Link href="#ai-cmo" className="text-base font-bold text-[#111111]" onClick={() => setMobileMenuOpen(false)}>AI CMO</Link>
            
            <div>
              <div className="text-base font-bold text-[#111111] mb-3">Agents</div>
              <div className="pl-3 grid grid-cols-2 gap-y-3 gap-x-4">
                {AGENTS.map((agent, i) => (
                  <Link key={i} href="#product" className="text-sm font-semibold text-[#5A5A5A] hover:text-[#800020]" onClick={() => setMobileMenuOpen(false)}>
                    {agent.name}
                  </Link>
                ))}
              </div>
            </div>

            <div>
              <div className="text-base font-bold text-[#111111] mb-3 mt-2">Integrations</div>
              <div className="pl-3 grid grid-cols-2 gap-y-3 gap-x-4">
                {INTEGRATIONS.map((int, i) => (
                  <Link key={i} href="#integrations" className="text-sm font-semibold text-[#5A5A5A] hover:text-[#800020]" onClick={() => setMobileMenuOpen(false)}>
                    {int.name}
                  </Link>
                ))}
              </div>
            </div>

            <Link href="#solutions" className="text-base font-bold text-[#111111] mt-2" onClick={() => setMobileMenuOpen(false)}>Solutions</Link>
            <Link href="/#pricing" className="text-base font-bold text-[#111111]" onClick={() => setMobileMenuOpen(false)}>Pricing</Link>
          </nav>
          <div className="flex flex-col gap-4 pt-4 border-t border-[#E8E4DC]">
            <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-login')); setMobileMenuOpen(false); }}>
              <Button variant="outline" className="w-full justify-center h-12 border-[#E8E4DC] text-[#111111] font-bold text-base">Log in</Button>
            </Link>
            <Link href="#" onClick={(e) => { e.preventDefault(); window.dispatchEvent(new Event('open-auth-signup')); setMobileMenuOpen(false); }}>
              <Button className="w-full justify-center h-12 bg-[#800020] hover:bg-[#5C0017] text-white font-bold text-base border-none shadow-sm shadow-[#800020]/20">Get Started</Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  )
}

export function MarketingFooter() {
  return (
    <footer className="bg-white border-t border-[#E8E4DC] pt-20 pb-10 px-6 lg:px-8">
      <div className="max-w-[1400px] mx-auto grid grid-cols-2 md:grid-cols-5 gap-12 mb-16">
        <div className="col-span-2 md:col-span-1 space-y-4">
          <Link href="/landingpage" className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-[#800020] flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-white" />
            </div>
            <span className="font-bold text-lg tracking-tight text-[#111111]">StandBharat</span>
          </Link>
          <p className="text-[#5A5A5A] text-sm font-medium pr-4 leading-relaxed">The AI marketing operating system for modern businesses.</p>
        </div>
        <div>
          <h4 className="font-bold text-[#111111] text-sm mb-6">Product</h4>
          <ul className="space-y-4 text-sm font-medium text-[#5A5A5A]">
            <li><Link href="#ai-cmo" className="hover:text-[#800020] transition-colors">AI CMO</Link></li>
            <li><Link href="#product" className="hover:text-[#800020] transition-colors">Brand Brain</Link></li>
            <li><Link href="#product" className="hover:text-[#800020] transition-colors">Agents</Link></li>
            <li><Link href="#how-it-works" className="hover:text-[#800020] transition-colors">Workflows</Link></li>
            <li><Link href="#product" className="hover:text-[#800020] transition-colors">Content</Link></li>
            <li><Link href="#product" className="hover:text-[#800020] transition-colors">Analytics</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold text-[#111111] text-sm mb-6">Company</h4>
          <ul className="space-y-4 text-sm font-medium text-[#5A5A5A]">
            <li><Link href="#" className="hover:text-[#800020] transition-colors">About</Link></li>
            <li><Link href="#" className="hover:text-[#800020] transition-colors">Careers</Link></li>
            <li><Link href="#" className="hover:text-[#800020] transition-colors">Contact</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold text-[#111111] text-sm mb-6">Resources</h4>
          <ul className="space-y-4 text-sm font-medium text-[#5A5A5A]">
            <li><Link href="#" className="hover:text-[#800020] transition-colors">Documentation</Link></li>
            <li><Link href="#" className="hover:text-[#800020] transition-colors">Blog</Link></li>
            <li><Link href="#" className="hover:text-[#800020] transition-colors">Help Center</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold text-[#111111] text-sm mb-6">Legal</h4>
          <ul className="space-y-4 text-sm font-medium text-[#5A5A5A]">
            <li><Link href="#" className="hover:text-[#800020] transition-colors">Privacy</Link></li>
            <li><Link href="#" className="hover:text-[#800020] transition-colors">Terms</Link></li>
            <li><Link href="#" className="hover:text-[#800020] transition-colors">Cookies</Link></li>
          </ul>
        </div>
      </div>
      <div className="max-w-[1400px] mx-auto pt-8 border-t border-[#E8E4DC] flex justify-between items-center text-sm font-medium text-[#858585]">
        <div>&copy; 2026 StandBharat. All rights reserved.</div>
      </div>
    </footer>
  )
}



