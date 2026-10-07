"use client"
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { LayoutDashboard, MessageSquare, Brain, Bot, Network, Target, PenTool, Calendar as CalendarIcon, Megaphone, BarChart3, IndianRupee, Swords, CheckSquare, Plug, Settings, Menu, X } from 'lucide-react'
import { useAuth } from '@/lib/providers/MockProvider'
import { useEffect, useState } from 'react'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const { authState, activeWorkspace, activeBrand, setAuthState, logout } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    if (authState === 'loggedOut') {
      router.push('/')
    }
  }, [authState, router])

  useEffect(() => {
    setMobileMenuOpen(false)
  }, [pathname])

  if (authState === 'loading') return <div className="h-screen flex items-center justify-center">Loading...</div>
  if (authState === 'loggedOut') return null

  const navigationGroups = [
    {
      label: 'COMMAND',
      items: [
        { name: 'Command Center', href: '/app/command-center', icon: LayoutDashboard },
        { name: 'AI CMO', href: '/app/ai-cmo', icon: MessageSquare },
      ]
    },
    {
      label: 'INTELLIGENCE',
      items: [
        { name: 'Brand Brain', href: '/app/brand-brain', icon: Brain },
        { name: 'Agents', href: '/app/agents', icon: Bot },
        { name: 'Opportunities', href: '/app/opportunities', icon: Target },
        { name: 'Competitors', href: '/app/competitors', icon: Swords },
      ]
    },
    {
      label: 'EXECUTION',
      items: [
        { name: 'Workflows', href: '/app/workflows', icon: Network },
        { name: 'Content', href: '/app/content', icon: PenTool },
        { name: 'Calendar', href: '/app/calendar', icon: CalendarIcon },
        { name: 'Campaigns', href: '/app/campaigns', icon: Megaphone },
        { name: 'Approvals', href: '/app/approvals', icon: CheckSquare },
      ]
    },
    {
      label: 'MEASUREMENT',
      items: [
        { name: 'Analytics', href: '/app/analytics', icon: BarChart3 },
        { name: 'Revenue', href: '/app/revenue', icon: IndianRupee },
      ]
    },
    {
      label: 'SYSTEM',
      items: [
        { name: 'Integrations', href: '/app/integrations', icon: Plug },
        { name: 'Settings', href: '/app/settings', icon: Settings },
      ]
    }
  ]

  const SidebarContent = () => (
    <>
      <div className="p-4 border-b border-[var(--color-border-primary)] flex justify-between items-center h-16">
        <div className="font-bold text-lg text-[var(--color-brand-accent)] tracking-tight">StandBharat</div>
        <button className="md:hidden text-[var(--color-text-tertiary)]" onClick={() => setMobileMenuOpen(false)}>
          <X className="h-5 w-5" />
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {navigationGroups.map((group) => (
          <div key={group.label}>
            <h3 className="px-3 text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">
              {group.label}
            </h3>
            <div className="space-y-1">
              {group.items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
                return (
                  <Link 
                    key={item.name} 
                    href={item.href} 
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive 
                        ? 'bg-[var(--color-bg-subtle)] text-[var(--color-brand-accent)]' 
                        : 'text-[var(--color-text-tertiary)] hover:bg-[var(--color-bg-subtle)] hover:text-[var(--color-text-primary)]'
                    }`}
                  >
                    <item.icon className={`mr-3 h-4 w-4 ${isActive ? 'text-[var(--color-brand-accent)]' : 'text-[var(--color-text-muted)]'}`} />
                    {item.name}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </nav>
      <div className="p-4 border-t border-[var(--color-border-primary)] bg-[var(--color-bg-primary)]">
        <div className="flex items-center justify-between">
          <div className="flex flex-col min-w-0">
            <span className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">Workspace</span>
            <span className="text-sm font-semibold text-[var(--color-text-primary)] truncate">{activeWorkspace?.name || 'Loading...'}</span>
          </div>
          <button className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors" onClick={async () => { await logout(); router.push('/landingpage') }}>Logout</button>
        </div>
      </div>
    </>
  )

  return (
    <div className="flex h-screen bg-[var(--color-bg-primary)] overflow-hidden font-sans">
      {/* Mobile Sidebar Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 md:hidden transition-opacity" onClick={() => setMobileMenuOpen(false)} />
      )}
      
      {/* Mobile Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-[var(--color-bg-surface)] shadow-2xl transform transition-transform duration-300 ease-in-out md:hidden flex flex-col ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <SidebarContent />
      </div>

      {/* Desktop Sidebar */}
      <div className="w-64 bg-[var(--color-bg-surface)] border-r border-[var(--color-border-primary)] flex-col flex-shrink-0 hidden md:flex shadow-sm z-10">
        <SidebarContent />
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 bg-[var(--color-bg-primary)]">
        <header className="h-16 bg-[var(--color-bg-surface)] border-b border-[var(--color-border-primary)] flex items-center px-4 md:px-8 justify-between flex-shrink-0 z-0">
          <div className="flex items-center">
            <button className="md:hidden text-[var(--color-text-tertiary)] mr-4 hover:text-[var(--color-text-primary)]" onClick={() => setMobileMenuOpen(true)}>
              <Menu className="h-5 w-5" />
            </button>
            <div className="flex flex-col">
              <div className="flex items-center text-xs font-medium text-[var(--color-text-muted)] mb-0.5">
                <span>{activeWorkspace?.name || 'Workspace'}</span>
                <span className="mx-2">/</span>
                <span className="text-[var(--color-text-tertiary)]">{activeBrand?.name || 'Brand'}</span>
              </div>
              <div className="text-lg font-semibold text-[var(--color-text-primary)] tracking-tight">
                {pathname.split('/').pop()?.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') || 'Dashboard'}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
             <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[var(--color-bg-subtle)] border border-[var(--color-border-primary)]">
               <span className="text-sm font-medium leading-none text-[var(--color-text-primary)]">A</span>
             </span>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
