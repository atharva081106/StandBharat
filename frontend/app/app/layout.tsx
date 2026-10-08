"use client"
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAppProvider } from '@/lib/providers'
import { useEffect, useState } from 'react'
import Image from 'next/image'
import { Bell, Search, Settings, ChevronDown, Activity, Sparkles, Check, X } from 'lucide-react'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { auth, orchestrator, notifications } = useAppProvider()
  const { authState, user, activeWorkspace, activeBrand, logout } = auth
  const orchestratorProvider = orchestrator
  const [showNotifications, setShowNotifications] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [isSearching, setIsSearching] = useState(false)

  useEffect(() => {
    if (searchQuery.length >= 2) {
      const delay = setTimeout(async () => {
        setIsSearching(true)
        try {
          const res = await fetch('/api/search?q=' + encodeURIComponent(searchQuery), { headers: { 'X-Workspace-ID': activeWorkspace?.id, 'X-Brand-ID': activeBrand?.id }})
          if (res.ok) {
            setSearchResults(await res.json())
          }
        } finally {
          setIsSearching(false)
        }
      }, 300)
      return () => clearTimeout(delay)
    } else {
      setSearchResults([])
    }
  }, [searchQuery, activeWorkspace?.id, activeBrand?.id])
  
  const [orchestratorConfig, setOrchestratorConfig] = useState<any>(null)

  useEffect(() => {
    if (authState === 'loggedOut') {
      router.push('/')
    }
  }, [authState, router])

  useEffect(() => {
    async function fetchStatus() {
      try {
        const config = await orchestratorProvider.getStatus()
        setOrchestratorConfig(config)
      } catch (e) {}
    }
    fetchStatus()
  }, [])

  if (authState === 'loading') return <div className="h-screen flex items-center justify-center bg-[#171515] text-[#F5F3F1]">Loading workspace...</div>
  if (authState === 'loggedOut') return null

  return (
    <div className="flex flex-col h-screen bg-[#171515] overflow-hidden font-sans text-[#F5F3F1] selection:bg-[#8F0028] selection:text-white">
      {/* Top Bar */}
      <header className="h-[52px] bg-[#1C1A1A] border-b border-[#373333] flex items-center justify-between px-4 shrink-0 z-50">
        
        {/* LEFT: Logo & Workspace */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Image src="/logo.jpg" alt="StandBharat Logo" width={28} height={28} className="rounded-md object-contain border border-white/10" />
            <span className="font-bold text-[15px] tracking-tight">StandBharat <ChevronDown className="w-3 h-3 inline text-[#A9A4A0]" /></span>
          </div>
          
          <div className="h-4 w-px bg-[#373333]"></div>
          
          <div className="flex items-center gap-2 text-[13px]">
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-[#242222] border border-[#373333] hover:bg-[#2A2828] cursor-pointer transition-colors">
              <Sparkles className="w-3.5 h-3.5 text-[#A9A4A0]" />
              <span className="font-medium">{activeWorkspace?.name || 'Workspace'}</span>
              <ChevronDown className="w-3 h-3 text-[#A9A4A0]" />
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md hover:bg-[#242222] cursor-pointer transition-colors text-[#A9A4A0]">
              <Activity className="w-3.5 h-3.5" />
              <span className="font-medium">Agent Log</span>
            </div>
          </div>
        </div>

        {/* CENTER: AI CMO Status */}
        <div className="hidden md:flex items-center gap-2 absolute left-1/2 -translate-x-1/2">
           <div className="h-2 w-2 rounded-full bg-[#00A650] animate-pulse"></div>
           <span className="text-[13px] font-medium text-[#A9A4A0]">
             AI CMO is analyzing <span className="text-[#F5F3F1]">{activeBrand?.website_url?.replace(/^https?:\/\//,'') || activeBrand?.name || 'brand'}</span>...
           </span>
        </div>

        {/* RIGHT: Search & User */}
        <div className="flex items-center gap-3">
          <div className="relative hidden lg:block">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-[#A9A4A0]" />
            <input 
              type="text" 
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search or ask anything..." 
              className="w-64 bg-[#242222] border border-[#373333] rounded-md py-1.5 pl-8 pr-3 text-[13px] text-[#F5F3F1] placeholder:text-[#A9A4A0] focus:outline-none focus:border-[#8F0028] transition-colors"
            />
            {searchQuery.length >= 2 && (
              <div className="absolute top-full left-0 mt-1 w-full bg-[#1C1A1A] border border-[#373333] rounded-md shadow-lg overflow-hidden z-50 flex flex-col max-h-[300px]">
                {isSearching ? (
                  <div className="p-3 text-[12px] text-[#A9A4A0] text-center">Searching...</div>
                ) : searchResults.length === 0 ? (
                  <div className="p-3 text-[12px] text-[#A9A4A0] text-center">No results found</div>
                ) : (
                  <div className="overflow-y-auto">
                    {searchResults.map(res => (
                      <Link href={res.url} key={res.id} onClick={() => setSearchQuery('')} className="block p-2 hover:bg-[#2A2828] border-b border-[#373333] last:border-0 transition-colors">
                        <div className="flex justify-between items-start">
                          <span className="font-semibold text-[13px] text-[#F5F3F1]">{res.title}</span>
                          <span className="text-[10px] uppercase text-[#A9A4A0] px-1 bg-[#242222] rounded">{res.type}</span>
                        </div>
                        {res.description && <p className="text-[11px] text-[#A9A4A0] line-clamp-1 mt-0.5">{res.description}</p>}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="h-8 w-8 rounded-md flex items-center justify-center hover:bg-[#242222] text-[#A9A4A0] transition-colors relative"
            >
              <Bell className="w-4 h-4" />
              {notifications?.unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              )}
            </button>
            {showNotifications && (
              <div className="absolute right-0 top-full mt-2 w-80 bg-[#1C1A1A] border border-[#373333] rounded-md shadow-lg overflow-hidden z-50 flex flex-col max-h-[400px]">
                <div className="px-4 py-2 border-b border-[#373333] flex justify-between items-center bg-[#242222]">
                  <span className="text-[13px] font-semibold text-[#F5F3F1]">Notifications</span>
                  <button onClick={() => notifications.markAllAsRead()} className="text-[11px] text-[#A9A4A0] hover:text-[#F5F3F1]">Mark all read</button>
                </div>
                <div className="overflow-y-auto flex-1 p-2 space-y-1">
                  {notifications?.notifications?.length === 0 ? (
                    <div className="p-4 text-center text-[12px] text-[#A9A4A0]">No notifications</div>
                  ) : (
                    notifications?.notifications?.map((n: any) => (
                      <div key={n.id} onClick={() => notifications.markAsRead(n.id)} className={`p-3 rounded-md text-[12px] cursor-pointer transition-colors ${n.read ? 'bg-transparent hover:bg-[#242222]' : 'bg-[#2A2828] hover:bg-[#373333]'}`}>
                         <div className="flex justify-between mb-1">
                           <span className="font-semibold text-[#F5F3F1]">{n.title}</span>
                           <span className="text-[10px] text-[#A9A4A0]">{new Date(n.created_at).toLocaleDateString()}</span>
                         </div>
                         <p className="text-[#A9A4A0] line-clamp-2">{n.message}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
          <div className="h-4 w-px bg-[#373333]"></div>
          <div className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity" onClick={async () => { await logout(); router.push('/') }}>
            <div className="h-7 w-7 rounded-full bg-indigo-600 flex items-center justify-center text-[11px] font-bold text-white shrink-0">
              {user?.name?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className="hidden lg:flex flex-col">
              <span className="text-[12px] font-semibold leading-none">{user?.name || 'User'}</span>
              <span className="text-[10px] text-[#A9A4A0] leading-none mt-1">Growth Plan</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace Area (The 4 columns go here) */}
      <main className="flex-1 flex overflow-hidden bg-[#171515]">
        {children}
      </main>
    </div>
  )
}
