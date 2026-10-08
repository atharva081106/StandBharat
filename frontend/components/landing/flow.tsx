'use client'

import { useRef } from 'react'
import gsap from 'gsap'
import { useGSAP } from '@gsap/react'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { ArrowDown, ArrowRight, CheckCircle2, Crown, FileText, Search, PenTool, BarChart3, Rocket, MessageSquare, Megaphone, ChevronRight } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'

gsap.registerPlugin(ScrollTrigger, useGSAP)

function TiltCard({ children, className }: { children: React.ReactNode, className?: string }) {
  const cardRef = useRef<HTMLDivElement>(null)
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const centerX = rect.width / 2
    const centerY = rect.height / 2
    
    const rotateX = ((y - centerY) / centerY) * -8
    const rotateY = ((x - centerX) / centerX) * 8
    
    cardRef.current.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`
  }

  const handleMouseLeave = () => {
    if (!cardRef.current) return
    cardRef.current.style.transform = 'perspective(1200px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)'
  }

  return (
    <div 
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`transition-transform duration-300 ease-out will-change-transform ${className || ''}`}
      style={{ transformStyle: 'preserve-3d' }}
    >
      {children}
    </div>
  )
}

const BrandLogos = {
  WordPress: <svg viewBox="0 0 24 24" fill="#21759b" className="w-8 h-8"><path d="M12.158 12.786l-2.698 7.84c.806.236 1.657.365 2.54.365 1.047 0 2.05-.18 2.986-.51-.024-.037-.046-.078-.065-.123l-2.762-7.57zM3.008 12c0 3.56 2.07 6.634 5.068 8.092L3.788 8.341c-.516 1.117-.78 2.354-.78 3.659zm14.372-4.505c.813 0 1.415.602 1.415 1.484 0 .978-.477 2.106-.954 3.31l-1.954 5.372c2.046-1.572 3.36-4.04 3.36-6.84 0-1.838-.574-3.535-1.55-4.945-.045.025-.09.055-.136.088-.517.382-1.285 1.144-1.285 1.528zm-5.464 4.88l1.458-4.25c.18-.528.27-.98.27-1.355 0-.453-.18-.755-.54-.906-.18-.075-.405-.113-.675-.113-.27 0-.585.038-.945.113v-1.13c.72-.075 1.35-.113 1.89-.113 1.17 0 2.07.302 2.7.906.63.604.945 1.434.945 2.49 0 .83-.18 1.66-.54 2.49l-4.568 12.98h-1.53l-2.835-8.25-2.835 8.25h-1.53l-4.568-12.98c-.36-.83-.54-1.66-.54-2.49 0-1.056.315-1.886.945-2.49.63-.604 1.53-.906 2.7-.906.54 0 1.17.038 1.89.113v1.13c-.36-.075-.675-.113-.945-.113-.27 0-.495.038-.675.113-.36.15-.54.452-.54.905 0 .377.09.83.27 1.358l2.97 8.64h.045l2.25-6.525-1.53-4.44h2.295l2.25 6.525h.045zM12 0C5.383 0 0 5.383 0 12s5.383 12 12 12 12-5.383 12-12S18.617 0 12 0z"/></svg>,
  Webflow: <svg viewBox="0 0 24 24" fill="#4353ff" className="w-8 h-8"><path d="M24 6.786l-2.091 10.429H18.57l-1.928-8.893h-.054l-1.928 8.893h-3.375L9.303 8.32h-.053l-1.93 8.894H4.018L1.928 6.786h3.428l1.34 6.91h.053l1.875-6.91h3.322l1.875 6.91h.053l1.34-6.91H24z"/></svg>,
  Framer: <svg viewBox="0 0 24 24" fill="#ffffff" className="w-8 h-8"><path d="M12 0H4v8h8L4 16h8v8l8-8h-8l8-8z"/></svg>,
  LinkedIn: <svg viewBox="0 0 24 24" fill="#0077b5" className="w-8 h-8"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z"/></svg>,
  Twitter: <svg viewBox="0 0 24 24" fill="#ffffff" className="w-8 h-8"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>,
  Slack: <svg viewBox="0 0 24 24" fill="#E01E5A" className="w-8 h-8"><path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zm1.271 0a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zm0 1.271a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zm10.122 2.52a2.528 2.528 0 0 1 2.522-2.52 2.528 2.528 0 0 1 2.521 2.52 2.528 2.528 0 0 1-2.521 2.521h-2.522V8.833zm-1.271 0a2.528 2.528 0 0 1-2.521 2.52 2.528 2.528 0 0 1-2.521-2.52V2.522A2.528 2.528 0 0 1 15.166 0a2.528 2.528 0 0 1 2.521 2.522v6.311zM15.166 18.958a2.528 2.528 0 0 1 2.521 2.522 2.528 2.528 0 0 1-2.521 2.52h-2.521v-2.522zm0-1.271a2.528 2.528 0 0 1-2.521-2.521 2.528 2.528 0 0 1 2.521-2.52h6.312A2.528 2.528 0 0 1 24 15.166a2.528 2.528 0 0 1-2.521 2.52H15.166z"/></svg>,
  GoogleAnalytics: <svg viewBox="0 0 24 24" fill="#f9ab00" className="w-8 h-8"><path d="M12.016 11.171v8.528h-3.66v-8.528h3.66zm6.305-6.868v15.396h-3.659V4.303h3.66zm-12.61 11.23v4.166h-3.66v-4.166h3.66z"/></svg>,
  Github: <svg viewBox="0 0 24 24" fill="#ffffff" className="w-8 h-8"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>,
  Wix: <svg viewBox="0 0 24 24" fill="#ffffff" className="w-8 h-8"><path d="M12.83 9.47L11.5 15.65h-.05l-1.33-6.18h-2l-1.33 6.18h-.05L5.4 9.47H3l2 8.76h2.2l1.35-6h.05l1.35 6h2.2l2-8.76h-2.4zm3.92 5.17l-.87-3.15h-.05l-.87 3.15h1.79zm-2.43 3.59h3.07l.38 1.33h2.32L17.5 9.47h-2.35l-2.6 10.09h2.27l.37-1.33zM21 9.47l-2.02 10.09h2.3l2.02-10.09H21z"/></svg>,
  WhatsApp: <svg viewBox="0 0 24 24" fill="#25D366" className="w-8 h-8"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>,
  Telegram: <svg viewBox="0 0 24 24" fill="#0088cc" className="w-8 h-8"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>,
  TikTok: <svg viewBox="0 0 24 24" fill="#ffffff" className="w-8 h-8"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 15.71a6.34 6.34 0 0 0 11.14 4.15V9.45a8.27 8.27 0 0 0 4.7 1.38V7.36a4.84 4.84 0 0 1-1.25-.67z"/></svg>,
  Instagram: <svg viewBox="0 0 24 24" fill="#E1306C" className="w-8 h-8"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>,
  YouTube: <svg viewBox="0 0 24 24" fill="#FF0000" className="w-8 h-8"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>,
  GoogleSearchConsole: <svg viewBox="0 0 24 24" fill="#4285F4" className="w-8 h-8"><path d="M12.01 2.01c-5.52 0-10 4.48-10 10s4.48 10 10 10 10-4.48 10-10-4.48-10-10-10zM13 18.01h-2v-2h2v2zm0-4h-2v-6h2v6z"/></svg>,
  Sanity: <svg viewBox="0 0 24 24" fill="#F03E2F" className="w-8 h-8"><path d="M16.63 7.62c-2.07-1.1-4.78-1.58-7.79-.67a8.55 8.55 0 0 0-5.82 5.86 8.58 8.58 0 0 0 .67 7.79 8.54 8.54 0 0 0 5.85 3.39c2.08 1.1 4.79 1.57 7.8.66a8.54 8.54 0 0 0 5.81-5.86 8.58 8.58 0 0 0-.67-7.79 8.51 8.51 0 0 0-5.85-3.38zm-1.89 12.02c-1.44 1.16-3.4 1.37-5.2.42-1.8-.95-2.77-2.73-2.6-4.72.17-1.99 1.48-3.6 3.48-4.27a5.53 5.53 0 0 1 5.2-.42c1.8.95 2.76 2.74 2.59 4.72-.18 1.99-1.48 3.6-3.47 4.27zm1.18-8.89a6.6 6.6 0 0 1-.9 2.21c-.4.63-.95 1.15-1.58 1.46-.64.32-1.36.41-2.08.26a4.2 4.2 0 0 1-1.83-.91c-.5-.45-.88-1.02-1.08-1.66-.2-.65-.18-1.35.06-1.98a4.19 4.19 0 0 1 1.25-1.63c.53-.44 1.16-.72 1.83-.81.67-.09 1.36.03 1.96.34.6.3 1.1.77 1.45 1.34.34.58.5 1.26.44 1.94a6.57 6.57 0 0 1-1.05 3.03l2.84 2.84a8.62 8.62 0 0 0-1.31-6.43z"/></svg>
}

const INTEGRATIONS = [
  { name: 'LinkedIn', icon: BrandLogos.LinkedIn, status: 'Connected', color: '#168A5B', bg: '#168A5B/10' },
  { name: 'WordPress', icon: BrandLogos.WordPress, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'X (Twitter)', icon: BrandLogos.Twitter, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'Webflow', icon: BrandLogos.Webflow, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'Framer', icon: BrandLogos.Framer, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'Wix', icon: BrandLogos.Wix, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'Sanity', icon: BrandLogos.Sanity, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'Google Search Console', icon: BrandLogos.GoogleSearchConsole, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'Google Analytics', icon: BrandLogos.GoogleAnalytics, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'GitHub', icon: BrandLogos.Github, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'WhatsApp', icon: BrandLogos.WhatsApp, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'Telegram', icon: BrandLogos.Telegram, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'Slack', icon: BrandLogos.Slack, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'TikTok', icon: BrandLogos.TikTok, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'Instagram', icon: BrandLogos.Instagram, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
  { name: 'YouTube', icon: BrandLogos.YouTube, status: 'Coming Soon', color: '#858585', bg: '#1A1A1A' },
]

const AGENTS = [
  { name: 'Research Agent', desc: 'Market & audience research', icon: Search, color: '#4285F4' },
  { name: 'Competitor Agent', desc: 'Competitor analysis', icon: Search, color: '#EA4335' },
  { name: 'Growth Agent', desc: 'Finds opportunities', icon: BarChart3, color: '#34A853' },
  { name: 'Content Strategy Agent', desc: 'Creates content plans', icon: FileText, color: '#9333EA' },
  { name: 'Writer Agent', desc: 'Drafts content', icon: PenTool, color: '#FBBC04' },
  { name: 'SEO Agent', desc: 'Search optimization', icon: Search, color: '#E91E63' },
  { name: 'Campaign Agent', desc: 'Runs campaigns', icon: Megaphone, color: '#4285F4' },
  { name: 'Performance Agent', desc: 'Analyzes results', icon: BarChart3, color: '#34A853' },
]

export function WorkflowFlow() {
  const container = useRef<HTMLDivElement>(null)

  useGSAP(() => {
    const parallaxElements = gsap.utils.toArray('.gsap-parallax') as HTMLElement[]
    parallaxElements.forEach((el) => {
      const speed = parseFloat(el.dataset.speed || '1')
      gsap.fromTo(el,
        { y: -30 * speed },
        {
          y: 30 * speed,
          ease: 'none',
          scrollTrigger: {
            trigger: el.closest('.gsap-parallax-container') || el.parentElement,
            start: 'top bottom',
            end: 'bottom top',
            scrub: true
          }
        }
      )
    })
  }, { scope: container })

  return (
    <div ref={container} className="bg-[#000000] text-white py-32 px-6 lg:px-8 relative overflow-hidden font-sans border-y border-white/5">
      
      {/* Background Decorative Gradients */}
      <div className="absolute inset-0 bg-[url('https://res.cloudinary.com/djp1xhexg/image/upload/v1727788414/grid_czvjio.svg')] bg-center opacity-10" style={{ maskImage: 'linear-gradient(to bottom, rgba(0,0,0,1), rgba(0,0,0,0) 100%)', WebkitMaskImage: 'linear-gradient(to bottom, rgba(0,0,0,1), rgba(0,0,0,0) 100%)' }} />
      
      <div className="max-w-[1200px] mx-auto flex flex-col relative z-10">
        
        {/* Step 1: Research */}
        <div className="flex flex-col lg:flex-row gap-12 lg:gap-20 items-center justify-between">
          <div className="w-full lg:w-[45%] space-y-6">
            <div className="gsap-reveal">
              <div className="inline-flex items-center rounded-full px-4 py-1.5 text-[11px] font-bold uppercase tracking-widest text-white/80 bg-white/5 border border-white/10 shadow-sm">
                STEP 1 — RESEARCH
              </div>
            </div>
            <div className="gsap-reveal" data-delay="0.1">
              <h2 className="text-[36px] md:text-[46px] font-extrabold tracking-tight text-white leading-[1.1]">
                StandBharat researches and prepares all strategy documents <span className="text-white/40">first.</span>
              </h2>
            </div>
            <div className="gsap-reveal" data-delay="0.2">
              <p className="text-[#858585] text-lg font-medium">
                Your brand, market and competitors — analyzed into a complete strategic foundation.
              </p>
            </div>
            <div className="gsap-reveal pt-4" data-delay="0.3">
              <div className="flex flex-wrap gap-3">
                <span className="px-5 py-2.5 rounded-full text-xs font-bold bg-white text-[#000000] shadow-sm flex items-center gap-2 cursor-pointer hover:bg-white/90 transition-colors">
                  Product Information <ArrowRight className="w-3.5 h-3.5" />
                </span>
                <span className="px-5 py-2.5 rounded-full border border-white/10 text-xs font-bold bg-transparent text-white shadow-sm cursor-pointer hover:bg-white/5 transition-colors">
                  Marketing Strategy
                </span>
                <span className="px-5 py-2.5 rounded-full border border-white/10 text-xs font-bold bg-transparent text-white shadow-sm cursor-pointer hover:bg-white/5 transition-colors">
                  Competitor Analysis
                </span>
                <span className="px-5 py-2.5 rounded-full border border-white/10 text-xs font-bold bg-transparent text-white shadow-sm cursor-pointer hover:bg-white/5 transition-colors">
                  Brand Voice
                </span>
                <span className="px-5 py-2.5 rounded-full border border-white/10 text-xs font-bold bg-transparent text-white shadow-sm cursor-pointer hover:bg-white/5 transition-colors">
                  Content Strategy
                </span>
              </div>
            </div>
          </div>

          <div className="w-full lg:w-[50%] gsap-parallax-container">
            <div className="gsap-reveal gsap-parallax w-full" data-delay="0.3" data-speed="0.5">
              <TiltCard className="bg-[#0A0A0A] border border-white/5 rounded-3xl p-6 shadow-2xl relative flex">
                {/* Left list */}
                <div className="w-1/2 space-y-6 pr-4">
                  {[
                    { title: 'Product Information', color: '#4285F4', bg: '#4285F4/10', icon: FileText, active: true },
                    { title: 'Overview', color: '#858585', bg: '#1A1A1A', icon: FileText },
                    { title: 'What It Does', color: '#F59E0B', bg: '#F59E0B/10', icon: Rocket },
                    { title: 'Category', color: '#9333EA', bg: '#9333EA/10', icon: PenTool },
                    { title: 'Target Customers', color: '#FBBF24', bg: '#FBBF24/10', icon: Search },
                    { title: 'Business Model', color: '#E91E63', bg: '#E91E63/10', icon: BarChart3 }
                  ].map((item, i) => {
                    const Icon = item.icon
                    return (
                      <div key={i} className="flex gap-4 items-start">
                        <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border border-white/5" style={{ backgroundColor: item.active ? 'rgba(66, 133, 244, 0.1)' : 'transparent' }}>
                           <Icon className="w-5 h-5" style={{ color: item.color }} />
                        </div>
                        <div className="pt-1 w-full">
                          <div className={`text-sm font-bold mb-2 ${item.active ? 'text-white' : 'text-white/60'}`}>{item.title}</div>
                          {item.active ? (
                            <div className="text-[10px] text-white/40">Generated from your inputs</div>
                          ) : (
                            <>
                              <div className="h-1.5 bg-white/5 rounded-full w-full mb-1.5"></div>
                              <div className="h-1.5 bg-white/5 rounded-full w-2/3"></div>
                            </>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>

                {/* Right floating cards */}
                <div className="w-1/2 relative flex flex-col justify-end pl-2">
                  <div className="absolute top-0 right-0 w-full h-[180px] flex justify-end gap-2 perspective-[1000px] origin-top-right">
                     {/* Back card */}
                     <div className="gsap-parallax w-[120px] h-[160px] bg-[#111111] border border-white/10 rounded-xl p-3 shadow-xl transform rotate-12 translate-x-4 translate-y-4 opacity-50 z-0 flex flex-col" data-speed="-0.2">
                        <div className="text-[10px] font-bold text-white mb-2 leading-tight">Competitor<br/>Analysis</div>
                        <div className="space-y-1.5 w-full mt-auto">
                          <div className="h-1 bg-white/10 rounded-full w-full"></div>
                          <div className="h-1 bg-white/10 rounded-full w-4/5"></div>
                          <div className="h-1 bg-white/10 rounded-full w-full"></div>
                          <div className="h-1 bg-white/10 rounded-full w-2/3"></div>
                        </div>
                     </div>
                     {/* Middle card */}
                     <div className="gsap-parallax absolute top-0 right-8 w-[120px] h-[160px] bg-[#1A1A1A] border border-white/10 rounded-xl p-3 shadow-2xl transform rotate-6 translate-x-2 translate-y-2 z-10 flex flex-col" data-speed="-0.4">
                        <div className="text-[10px] font-bold text-white mb-2 leading-tight">Brand<br/>Voice</div>
                        <div className="space-y-1.5 w-full mt-auto">
                          <div className="h-1 bg-white/10 rounded-full w-full"></div>
                          <div className="h-1 bg-white/10 rounded-full w-5/6"></div>
                          <div className="h-1 bg-white/10 rounded-full w-full"></div>
                          <div className="h-1 bg-white/10 rounded-full w-3/4"></div>
                        </div>
                     </div>
                     {/* Front card */}
                     <div className="gsap-parallax absolute top-2 right-16 w-[140px] h-[180px] bg-white rounded-xl p-4 shadow-2xl transform -rotate-6 z-20 flex flex-col items-center border border-white/20" data-speed="-0.6">
                        <div className="flex items-center gap-1.5 mb-4 w-full">
                           <Image src="/logo.jpg" alt="StandBharat Logo" width={18} height={18} className="rounded object-contain brightness-90 contrast-125 border border-black/5" />
                           <div className="text-[9px] font-bold text-black tracking-tight">StandBharat</div>
                        </div>
                        <div className="text-xs font-extrabold text-black mb-3 leading-tight w-full">Go-To-Market Strategy</div>
                        <div className="space-y-2 w-full mt-auto">
                          <div className="h-1.5 bg-[#E8E4DC] rounded-full w-full"></div>
                          <div className="h-1.5 bg-[#E8E4DC] rounded-full w-5/6"></div>
                          <div className="h-1.5 bg-[#E8E4DC] rounded-full w-full"></div>
                          <div className="h-1.5 bg-[#E8E4DC] rounded-full w-4/5"></div>
                          <div className="h-1.5 bg-[#E8E4DC] rounded-full w-2/3"></div>
                        </div>
                     </div>
                  </div>

                  <div className="gsap-parallax bg-[#111111] border border-white/5 rounded-2xl p-5 shadow-lg mt-40 z-30" data-speed="-0.3">
                    <div className="text-xs font-bold text-white mb-4">5 Strategic Documents</div>
                    <div className="space-y-3">
                      {['Product Information', 'Marketing Strategy', 'Competitor Analysis', 'Brand Voice', 'Content Strategy'].map((doc, i) => (
                        <div key={i} className="flex items-center gap-3">
                          <CheckCircle2 className="w-4 h-4 text-[#168A5B]" />
                          <span className="text-[11px] font-medium text-white/80">{doc}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </TiltCard>
            </div>
          </div>
        </div>

        {/* Connecting Arrow */}
        <div className="flex justify-center h-20 relative my-6">
           <div className="w-[1px] h-full border-r border-dashed border-white/20"></div>
           <div className="absolute bottom-0 text-white/40 transform translate-y-1/2 bg-[#050505] px-2">
              <ArrowDown className="w-3 h-3" />
           </div>
        </div>

        {/* The Handoff */}
        <div className="flex flex-col items-center justify-center text-center relative z-10 gsap-reveal">
           <div className="bg-[#0A0A0A] border border-white/10 rounded-3xl pt-10 pb-8 px-12 shadow-2xl max-w-3xl mx-auto relative z-10 w-full border-t-0 mt-4">
             <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 rounded-full border border-white/10 bg-[#0A0A0A] flex items-center justify-center">
               <FileText className="w-4 h-4 text-white/60" />
             </div>
             <div className="text-[9px] font-bold text-[#E91E63] uppercase tracking-[0.3em] mb-4">THE HANDOFF</div>
             <h3 className="text-2xl font-extrabold mb-8 text-white leading-tight">Every agent reads these five documents<br/>before it writes a word.</h3>
             <div className="flex flex-wrap justify-center gap-3">
               {['product-info.md', 'marketing-strategy.md', 'competitor-analysis.md', 'brand-voice.md', 'content-strategy.md'].map(doc => (
                 <span key={doc} className="px-3 py-1.5 rounded-md border border-white/10 text-[10px] font-mono text-white/50 bg-[#111111] flex items-center gap-2">
                   <FileText className="w-3 h-3 text-white/30" />
                   {doc}
                 </span>
               ))}
             </div>
           </div>
        </div>

        {/* Connecting Arrow */}
        <div className="flex justify-center h-20 relative my-6">
           <div className="w-[1px] h-full border-r border-dashed border-white/20"></div>
           <div className="absolute bottom-0 text-white/40 transform translate-y-1/2 bg-[#000000] px-2">
              <ArrowDown className="w-3 h-3" />
           </div>
        </div>

        {/* Step 2: Execution */}
        <div className="flex flex-col lg:flex-row gap-12 lg:gap-20 items-center justify-between">
          <div className="w-full lg:w-[35%] space-y-6">
            <div className="gsap-reveal">
              <div className="inline-flex items-center rounded-full px-4 py-1.5 text-[11px] font-bold uppercase tracking-widest text-white/80 bg-white/5 border border-white/10 shadow-sm">
                STEP 2 — EXECUTION
              </div>
            </div>
            <div className="gsap-reveal" data-delay="0.1">
              <h2 className="text-[36px] md:text-[46px] font-extrabold tracking-tight text-white leading-[1.1]">
                All agents execute the strategy, channel by channel.
              </h2>
            </div>
            <div className="gsap-reveal" data-delay="0.2">
              <p className="text-[#858585] text-lg font-medium">
                Specialized agents turn strategy into high-quality, on-brand content across every channel.
              </p>
            </div>
          </div>

          <div className="w-full lg:w-[65%] gsap-parallax-container">
            <div className="gsap-reveal gsap-parallax w-full" data-delay="0.3" data-speed="0.4">
               <TiltCard className="bg-[#0A0A0A] border border-white/5 rounded-3xl p-8 pt-10 shadow-2xl relative">
                  
                  {/* AI CMO Top Block */}
                  <div className="flex justify-center mb-8 relative z-10">
                     <div className="bg-[#111111] border border-[#F59E0B]/30 rounded-2xl px-6 py-4 flex items-center gap-4 shadow-[0_0_30px_rgba(245,158,11,0.05)]">
                        <div className="w-12 h-12 bg-[#F59E0B]/10 rounded-xl flex items-center justify-center border border-[#F59E0B]/20">
                           <Crown className="w-6 h-6 text-[#F59E0B]" />
                        </div>
                        <div>
                           <div className="font-extrabold text-white text-lg">AI CMO</div>
                           <div className="text-xs text-white/50 max-w-[150px] leading-tight mt-1">Orchestrates agents and keeps everything aligned.</div>
                        </div>
                     </div>
                  </div>

                  {/* Connecting Routing Lines SVG */}
                  <div className="absolute top-[85px] left-0 w-full h-[125px] pointer-events-none opacity-50 z-0">
                     <svg width="100%" height="100%" preserveAspectRatio="none">
                        <defs>
                           <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
                              <path d="M0,0 L0,6 L6,3 z" fill="rgba(255,255,255,0.6)" />
                           </marker>
                        </defs>
                        <path d="M50% 0 L50% 30 L15% 30 L15% 85" stroke="rgba(255,255,255,0.3)" strokeWidth="1" fill="none" strokeDasharray="4 4" markerEnd="url(#arrowhead)" />
                        <path d="M50% 0 L50% 30 L40% 30 L40% 85" stroke="rgba(255,255,255,0.3)" strokeWidth="1" fill="none" strokeDasharray="4 4" markerEnd="url(#arrowhead)" />
                        <path d="M50% 0 L50% 30 L60% 30 L60% 85" stroke="rgba(255,255,255,0.3)" strokeWidth="1" fill="none" strokeDasharray="4 4" markerEnd="url(#arrowhead)" />
                        <path d="M50% 0 L50% 30 L85% 30 L85% 85" stroke="rgba(255,255,255,0.3)" strokeWidth="1" fill="none" strokeDasharray="4 4" markerEnd="url(#arrowhead)" />
                     </svg>
                  </div>

                  {/* Agent Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12 relative z-10">
                    {AGENTS.map((agent, i) => {
                      const Icon = agent.icon;
                      return (
                        <div key={agent.name} className="bg-[#111111] border border-white/5 rounded-xl p-5 hover:bg-[#151515] hover:border-white/20 transition-all duration-300">
                           <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style={{ backgroundColor: `${agent.color}15` }}>
                             <Icon className="w-5 h-5" style={{ color: agent.color }} />
                           </div>
                           <h4 className="text-[13px] font-bold text-white mb-1 leading-tight">{agent.name}</h4>
                           <div className="text-[11px] text-[#A1A1A1] mb-3">{agent.desc}</div>
                           <div className="flex items-center gap-1.5 mt-auto">
                              <div className="w-1.5 h-1.5 rounded-full bg-[#168A5B]"></div>
                              <div className="text-[10px] font-bold text-[#168A5B]">Ready</div>
                           </div>
                        </div>
                      )
                    })}
                  </div>
               </TiltCard>
            </div>
          </div>
        </div>

        {/* Connecting Arrow */}
        <div className="flex justify-center h-20 relative my-6">
           <div className="w-[1px] h-full border-r border-dashed border-white/20"></div>
           <div className="absolute bottom-0 text-white/40 transform translate-y-1/2 bg-[#000000] px-2">
              <ArrowDown className="w-3 h-3" />
           </div>
        </div>

        {/* Step 3: Publish */}
        <div className="flex flex-col lg:flex-row gap-12 lg:gap-20 items-center justify-between">
          <div className="w-full lg:w-[35%] space-y-6">
            <div className="gsap-reveal">
              <div className="inline-flex items-center rounded-full px-4 py-1.5 text-[11px] font-bold uppercase tracking-widest text-white/80 bg-white/5 border border-white/10 shadow-sm">
                STEP 3 — PUBLISH
              </div>
            </div>
            <div className="gsap-reveal" data-delay="0.1">
              <h2 className="text-[36px] md:text-[46px] font-extrabold tracking-tight text-white leading-[1.1]">
                Connect your stack.<br/>Publish without leaving it.
              </h2>
            </div>
            <div className="gsap-reveal" data-delay="0.2">
              <p className="text-[#858585] text-lg font-medium">
                Turn approved content into results across your favourite tools.
              </p>
            </div>
            <div className="gsap-reveal pt-4" data-delay="0.3">
               <span className="px-5 py-3 rounded-full text-sm font-bold bg-white text-[#050505] shadow-sm inline-flex items-center gap-2 cursor-pointer hover:bg-white/90 transition-colors">
                  Connect Integrations <ArrowRight className="w-4 h-4" />
                </span>
            </div>
          </div>

          <div className="w-full lg:w-[65%] gsap-parallax-container">
            <div className="gsap-reveal gsap-parallax w-full" data-delay="0.3" data-speed="0.3">
               <TiltCard className="bg-[#0A0A0A] border border-white/5 rounded-3xl p-8 pt-10 shadow-2xl relative">
                  <div className="grid grid-cols-3 md:grid-cols-4 gap-y-10 gap-x-6 text-center">
                     {INTEGRATIONS.map((int, i) => (
                        <div key={int.name} className="flex flex-col items-center gap-3">
                           {int.icon}
                           <div className="text-[11px] font-bold text-white/80 leading-tight">{int.name}</div>
                           <div className="px-2.5 py-1 rounded-full text-[8px] font-bold uppercase tracking-wide border border-white/5" style={{ backgroundColor: int.status === 'Connected' ? 'rgba(22, 138, 91, 0.1)' : '#111111', color: int.status === 'Connected' ? '#168A5B' : '#5A5A5A' }}>
                              {int.status}
                           </div>
                        </div>
                     ))}
                     
                     {/* More Integrations + */}
                     <div className="col-span-3 md:col-span-4 mt-2">
                        <div className="border border-dashed border-white/10 rounded-xl p-4 flex flex-col items-center justify-center gap-2 bg-[#111111]/50 h-full">
                           <div className="text-white/40 text-xl font-light">+</div>
                           <div className="text-[10px] font-bold text-white/40 leading-tight">More Integrations<br/>Coming Soon</div>
                        </div>
                     </div>
                  </div>
               </TiltCard>
            </div>
          </div>
        </div>

        {/* Connecting Arrow */}
        <div className="flex justify-center h-20 relative my-6">
           <div className="w-[1px] h-full border-r border-dashed border-white/20"></div>
           <div className="absolute bottom-0 text-white/40 transform translate-y-1/2 bg-[#000000] px-2">
              <ArrowDown className="w-3 h-3" />
           </div>
        </div>

        {/* Step 4: Measure */}
        <div className="flex flex-col lg:flex-row gap-12 lg:gap-20 items-center justify-between">
          <div className="w-full lg:w-[35%] space-y-6">
            <div className="gsap-reveal">
              <div className="inline-flex items-center rounded-full px-4 py-1.5 text-[11px] font-bold uppercase tracking-widest text-white/80 bg-white/5 border border-white/10 shadow-sm">
                STEP 4 — MEASURE
              </div>
            </div>
            <div className="gsap-reveal" data-delay="0.1">
              <h2 className="text-[36px] md:text-[46px] font-extrabold tracking-tight text-white leading-[1.1]">
                Performance Intelligence closes the loop.
              </h2>
            </div>
            <div className="gsap-reveal" data-delay="0.2">
              <p className="text-[#858585] text-lg font-medium">
                Once published, StandBharat continuously pulls engagement data back into the Brand Brain. The AI CMO analyzes what worked, generating new signals and growth opportunities for your next campaign.
              </p>
            </div>
          </div>

          <div className="w-full lg:w-[65%] relative gsap-parallax-container">
            <div className="gsap-reveal gsap-parallax w-full" data-delay="0.3" data-speed="0.4">
               <TiltCard className="bg-[#0A0A0A] border border-white/5 rounded-3xl p-8 pt-10 shadow-2xl relative">
                  <div className="bg-[#111111] border border-white/10 rounded-[24px] p-6 shadow-xl relative overflow-hidden group">
                     <div className="flex justify-between items-center mb-8 border-b border-white/5 pb-4">
                        <div className="flex items-center gap-3">
                           <div className="w-8 h-8 rounded-full bg-[#168A5B]/10 flex items-center justify-center">
                              <BarChart3 className="w-4 h-4 text-[#168A5B]" />
                           </div>
                           <div className="font-bold text-white">Brand Command Center</div>
                        </div>
                        <div className="text-[10px] bg-white/5 px-3 py-1 rounded-full text-white/60">Live Updates</div>
                     </div>
                     
                     <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="bg-[#1A1A1A] p-4 rounded-xl border border-white/5">
                           <div className="text-xs text-white/40 mb-1">Brand Visibility</div>
                           <div className="text-2xl font-bold text-white mb-2">78</div>
                           <div className="text-[10px] text-[#168A5B]">+12% this week</div>
                        </div>
                        <div className="bg-[#1A1A1A] p-4 rounded-xl border border-white/5">
                           <div className="text-xs text-white/40 mb-1">Audience Sentiment</div>
                           <div className="text-2xl font-bold text-white mb-2">92%</div>
                           <div className="text-[10px] text-[#168A5B]">+8% vs last mo</div>
                        </div>
                     </div>
                     
                     <div className="bg-[#1A1A1A] p-4 rounded-xl border border-[#F59E0B]/20 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-[#F59E0B]/5 rounded-full blur-[30px] -mr-10 -mt-10"></div>
                        <div className="flex items-center gap-2 mb-2">
                           <div className="w-2 h-2 rounded-full bg-[#F59E0B] animate-pulse"></div>
                           <div className="text-[10px] font-bold text-[#F59E0B] uppercase tracking-wider">Opportunity Detected</div>
                        </div>
                        <div className="text-sm font-bold text-white mb-1">High engagement on recent X thread</div>
                        <div className="text-xs text-white/60">The AI CMO recommends turning this topic into a long-form blog post.</div>
                        <button className="mt-3 px-3 py-1.5 bg-white text-black text-[10px] font-bold rounded-lg hover:bg-white/90 transition-colors">
                           Generate Draft
                        </button>
                     </div>
                  </div>
               </TiltCard>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
