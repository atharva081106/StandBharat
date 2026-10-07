import os
from pathlib import Path

BASE_DIR = Path("frontend")

def write_file(path, content):
    full_path = BASE_DIR / path
    os.makedirs(full_path.parent, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# --- app/app/layout.tsx ---
app_layout_tsx = """
"use client"
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { LayoutDashboard, MessageSquare, Brain, Bot, Network, Target, PenTool, Calendar as CalendarIcon, Megaphone, BarChart3, IndianRupee, Swords, CheckSquare, Plug, Settings } from 'lucide-react'
import { useAuth } from '@/lib/providers/MockProvider'
import { useEffect } from 'react'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const { authState, activeWorkspace, activeBrand, setAuthState } = useAuth()

  useEffect(() => {
    if (authState === 'loggedOut') {
      router.push('/login')
    }
  }, [authState, router])

  if (authState === 'loggedOut') return null

  const navigation = [
    { name: 'Command Center', href: '/app/command-center', icon: LayoutDashboard },
    { name: 'AI CMO', href: '/app/ai-cmo', icon: MessageSquare },
    { name: 'Brand Brain', href: '/app/brand-brain', icon: Brain },
    { name: 'Agents', href: '/app/agents', icon: Bot },
    { name: 'Workflows', href: '/app/workflows', icon: Network },
    { name: 'Opportunities', href: '/app/opportunities', icon: Target },
    { name: 'Content', href: '/app/content', icon: PenTool },
    { name: 'Calendar', href: '/app/calendar', icon: CalendarIcon },
    { name: 'Campaigns', href: '/app/campaigns', icon: Megaphone },
    { name: 'Analytics', href: '/app/analytics', icon: BarChart3 },
    { name: 'Revenue', href: '/app/revenue', icon: IndianRupee },
    { name: 'Competitors', href: '/app/competitors', icon: Swords },
    { name: 'Approvals', href: '/app/approvals', icon: CheckSquare },
  ]

  const settings = [
    { name: 'Integrations', href: '/app/integrations', icon: Plug },
    { name: 'Settings', href: '/app/settings', icon: Settings },
  ]

  return (
    <div className="flex h-screen bg-[#FAFAF8] overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-[#E5E5E5] flex flex-col flex-shrink-0 hidden md:flex">
        <div className="p-4 border-b border-[#E5E5E5]">
          <div className="font-bold text-lg text-orange-500">StandBharat</div>
        </div>
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          <div className="mb-4">
            {navigation.map((item) => (
              <Link key={item.name} href={item.href} className={`flex items-center px-3 py-2 rounded-md text-sm font-medium mb-1 ${pathname.startsWith(item.href) ? 'bg-[#111111] text-white' : 'text-[#525252] hover:bg-gray-100 hover:text-[#111111]'}`}>
                <item.icon className={`mr-3 h-4 w-4 ${pathname.startsWith(item.href) ? 'text-white' : 'text-[#737373]'}`} />
                {item.name}
              </Link>
            ))}
          </div>
          <div className="border-t border-[#E5E5E5] my-4"></div>
          {settings.map((item) => (
            <Link key={item.name} href={item.href} className={`flex items-center px-3 py-2 rounded-md text-sm font-medium mb-1 ${pathname.startsWith(item.href) ? 'bg-[#111111] text-white' : 'text-[#525252] hover:bg-gray-100 hover:text-[#111111]'}`}>
              <item.icon className={`mr-3 h-4 w-4 ${pathname.startsWith(item.href) ? 'text-white' : 'text-[#737373]'}`} />
              {item.name}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-[#E5E5E5]">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium truncate">{activeWorkspace?.name}</span>
            <button className="text-orange-500 hover:underline" onClick={() => { setAuthState('loggedOut'); router.push('/landingpage') }}>Logout</button>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 bg-white border-b border-[#E5E5E5] flex items-center px-6 justify-between flex-shrink-0">
          <div className="flex items-center text-sm font-medium text-[#737373]">
            {activeWorkspace?.name} <span className="mx-2">/</span> {activeBrand?.name}
          </div>
          <div className="flex items-center">
             <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-gray-200">
               <span className="text-sm font-medium leading-none text-gray-700">A</span>
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
"""
write_file("app/app/layout.tsx", app_layout_tsx)

# --- app/app/command-center/page.tsx ---
command_center_tsx = """
"use client"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { mockKPIs, mockOpportunities, mockApprovals } from '@/lib/mock/data'
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts'

const data = [
  { name: 'Mon', revenue: 4000, leads: 240 },
  { name: 'Tue', revenue: 3000, leads: 139 },
  { name: 'Wed', revenue: 2000, leads: 980 },
  { name: 'Thu', revenue: 2780, leads: 390 },
  { name: 'Fri', revenue: 1890, leads: 480 },
  { name: 'Sat', revenue: 2390, leads: 380 },
  { name: 'Sun', revenue: 3490, leads: 430 },
]

export default function CommandCenter() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Good morning, Atharva 👋</h1>
        <Badge variant="warning">DEMO DATA</Badge>
      </div>
      
      <p className="text-[#525252]">Here's what's happening with your marketing today.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Object.entries(mockKPIs).map(([key, data]) => (
          <Card key={key}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-[#737373] uppercase tracking-wider">{key.replace(/([A-Z])/g, ' $1').trim()}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.value}</div>
              <p className="text-xs text-green-600 mt-1">{data.change} from last period</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Performance Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                  <XAxis dataKey="name" stroke="#737373" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#737373" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${value}`} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E5E5E5' }} />
                  <Line type="monotone" dataKey="revenue" stroke="#f97316" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Next Best Action</CardTitle>
            </CardHeader>
            <CardContent>
              {mockOpportunities.slice(0,1).map(opp => (
                <div key={opp.id} className="space-y-4">
                  <p className="font-medium">{opp.title}</p>
                  <div className="flex gap-4 text-sm">
                    <div>
                      <span className="text-[#737373]">Impact:</span> <span className="font-medium text-orange-600">{opp.impact}</span>
                    </div>
                    <div>
                      <span className="text-[#737373]">Confidence:</span> <span className="font-medium">{opp.confidence}</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" className="w-full">Execute</Button>
                    <Button size="sm" variant="outline" className="w-full">Review</Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-red-50 text-red-800 rounded-md text-sm">
                  <span>Google Search Console not connected</span>
                  <a href="#" className="underline">Fix</a>
                </div>
                <div className="flex items-center justify-between p-3 bg-amber-50 text-amber-800 rounded-md text-sm">
                  <span>LinkedIn authorization required</span>
                  <a href="#" className="underline">Fix</a>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Agent Activity</CardTitle>
          </CardHeader>
          <CardContent>
             <div className="space-y-4">
               <div className="flex items-center gap-3">
                 <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                 <span className="text-sm"><b>Writer Agent</b> is drafting "Top 10 SEO Trends"</span>
               </div>
               <div className="flex items-center gap-3">
                 <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                 <span className="text-sm"><b>Analytics Agent</b> completed weekly report</span>
               </div>
               <div className="flex items-center gap-3">
                 <div className="h-2 w-2 bg-gray-300 rounded-full"></div>
                 <span className="text-sm"><b>SEO Agent</b> waiting for approval</span>
               </div>
             </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Pending Approvals</CardTitle>
          </CardHeader>
          <CardContent>
             <div className="space-y-4">
                {mockApprovals.map(app => (
                  <div key={app.id} className="flex items-center justify-between border-b border-[#E5E5E5] pb-3 last:border-0 last:pb-0">
                    <div>
                      <p className="text-sm font-medium">{app.title}</p>
                      <p className="text-xs text-[#737373]">{app.agent} • {app.requested}</p>
                    </div>
                    <Button size="sm" variant="outline">Review</Button>
                  </div>
                ))}
             </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
"""
write_file("app/app/command-center/page.tsx", command_center_tsx)

# --- app/app/ai-cmo/page.tsx ---
ai_cmo_tsx = """
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { MessageSquare, Send } from 'lucide-react'

export default function AICMO() {
  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col bg-white rounded-xl shadow-sm border border-[#E5E5E5] overflow-hidden">
      <div className="p-4 border-b border-[#E5E5E5] flex justify-between items-center bg-[#FAFAF8]">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-orange-500" /> AI CMO
          </h2>
          <p className="text-xs text-[#737373]">Your autonomous marketing strategist.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-green-500"></span>
          <span className="text-xs font-medium text-green-700">ONLINE</span>
        </div>
      </div>
      
      <div className="flex-1 p-6 overflow-y-auto space-y-6">
        <div className="flex flex-col items-end">
           <div className="bg-[#111111] text-white p-4 rounded-2xl rounded-tr-sm max-w-lg">
             <p className="text-sm">What should we focus on this week?</p>
           </div>
        </div>
        
        <div className="flex flex-col items-start">
           <div className="bg-[#FAFAF8] border border-[#E5E5E5] p-4 rounded-2xl rounded-tl-sm max-w-2xl">
             <p className="text-sm text-[#111111] mb-4">Your strongest opportunity is improving organic conversion on high-intent pages. I've analyzed our performance and found several quick wins.</p>
             <Card className="shadow-none bg-white">
                <div className="p-4 space-y-3">
                  <div className="font-medium text-sm">Target: "Skincare Guide" Landing Page</div>
                  <div className="flex gap-4 text-xs">
                    <span className="text-orange-600 font-medium">Impact: HIGH</span>
                    <span>Confidence: 87%</span>
                  </div>
                  <p className="text-xs text-[#525252]">The SEO Agent has identified 3 missing keywords and the Writer Agent has drafted section updates.</p>
                  <Button size="sm" className="w-full">Review Recommended Action</Button>
                </div>
             </Card>
           </div>
        </div>
      </div>
      
      <div className="p-4 border-t border-[#E5E5E5] bg-white">
        <div className="flex gap-2 mb-3 overflow-x-auto pb-2">
          {["Find my biggest growth opportunity", "Analyze my SEO", "Create a content strategy", "Analyze competitors"].map(p => (
            <button key={p} className="text-xs px-3 py-1.5 rounded-full border border-[#E5E5E5] bg-[#FAFAF8] text-[#525252] hover:bg-gray-100 whitespace-nowrap">
              {p}
            </button>
          ))}
        </div>
        <div className="relative">
          <Input placeholder="Ask your AI CMO..." className="pr-10 rounded-full bg-[#FAFAF8]" />
          <button className="absolute right-2 top-2 p-1 text-orange-500 hover:text-orange-600">
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
"""
write_file("app/app/ai-cmo/page.tsx", ai_cmo_tsx)

# --- app/app/brand-brain/page.tsx ---
brand_brain_tsx = """
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function BrandBrain() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Brand Brain</h1>
          <p className="text-[#525252]">The central knowledge base your AI agents use to understand your business.</p>
        </div>
        <div className="text-right">
          <div className="text-sm font-medium text-orange-500">82% Complete</div>
          <div className="w-32 h-2 bg-gray-200 rounded-full mt-1 overflow-hidden">
             <div className="h-full bg-orange-500 w-[82%]"></div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Business Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm text-[#525252]">
            <div><span className="font-medium text-[#111111]">Name:</span> Acme SaaS</div>
            <div><span className="font-medium text-[#111111]">Industry:</span> Software</div>
            <div><span className="font-medium text-[#111111]">Target:</span> B2B Enterprise</div>
            <button className="text-orange-500 hover:underline">Edit</button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Brand Voice</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex gap-2 flex-wrap">
              <Badge variant="secondary">Professional</Badge>
              <Badge variant="secondary">Authoritative</Badge>
              <Badge variant="secondary">Direct</Badge>
            </div>
            <p className="text-[#525252]">"We speak to technical leaders with clarity and confidence, avoiding fluff."</p>
            <button className="text-orange-500 hover:underline">Edit</button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Documents</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
             <div className="p-3 border border-[#E5E5E5] rounded-md text-sm flex justify-between items-center">
               <span className="truncate">Product_Whitepaper_2026.pdf</span>
               <Badge variant="success">Parsed</Badge>
             </div>
             <div className="p-3 border border-[#E5E5E5] rounded-md text-sm flex justify-between items-center">
               <span className="truncate">Style_Guide.docx</span>
               <Badge variant="success">Parsed</Badge>
             </div>
             <button className="text-orange-500 hover:underline text-sm font-medium mt-2">+ Upload Document</button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
"""
write_file("app/app/brand-brain/page.tsx", brand_brain_tsx)

print("App layout and main dashboard views generated.")
