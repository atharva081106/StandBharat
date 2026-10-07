import os
from pathlib import Path

BASE_DIR = Path("frontend")

def write_file(path, content):
    full_path = BASE_DIR / path
    os.makedirs(full_path.parent, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

pricing_tsx = """
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function Pricing() {
  return (
    <div className="min-h-screen flex flex-col bg-[#FAFAF8]">
      <header className="flex justify-between items-center px-8 py-6 border-b border-[#E5E5E5] bg-white">
        <Link href="/" className="font-bold text-xl tracking-tighter text-[#111111]">StandBharat</Link>
        <div className="flex space-x-4">
          <Link href="/login"><Button variant="ghost">Sign In</Button></Link>
          <Link href="/signup"><Button>Get Started</Button></Link>
        </div>
      </header>
      <main className="flex-1 flex flex-col items-center pt-24 pb-24 px-6">
        <h1 className="text-4xl font-bold tracking-tight text-[#111111]">Simple, transparent pricing</h1>
        <p className="mt-4 text-lg text-[#525252]">Start for free, upgrade when your AI team needs to scale.</p>
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full">
           <div className="bg-white p-8 rounded-xl border border-[#E5E5E5] shadow-sm">
             <h3 className="text-xl font-bold">Starter</h3>
             <p className="text-3xl font-bold mt-4">Free</p>
             <p className="text-[#525252] mt-2 text-sm">Basic AI agents for early stage.</p>
             <Button className="w-full mt-8" variant="outline">Current Plan</Button>
           </div>
           <div className="bg-white p-8 rounded-xl border-2 border-orange-500 shadow-md relative">
             <div className="absolute top-0 right-8 transform -translate-y-1/2 bg-orange-500 text-white px-3 py-1 text-xs font-bold rounded-full">POPULAR</div>
             <h3 className="text-xl font-bold">Growth</h3>
             <p className="text-3xl font-bold mt-4">₹4,999<span className="text-sm font-normal text-[#525252]">/mo</span></p>
             <p className="text-[#525252] mt-2 text-sm">Full autonomous marketing team.</p>
             <Button className="w-full mt-8">Upgrade</Button>
           </div>
           <div className="bg-white p-8 rounded-xl border border-[#E5E5E5] shadow-sm">
             <h3 className="text-xl font-bold">Enterprise</h3>
             <p className="text-3xl font-bold mt-4">Custom</p>
             <p className="text-[#525252] mt-2 text-sm">Dedicated models and SLAs.</p>
             <Button className="w-full mt-8" variant="outline">Contact Sales</Button>
           </div>
        </div>
      </main>
    </div>
  )
}
"""
write_file("app/pricing/page.tsx", pricing_tsx)

agent_id_tsx = """
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export default function AgentDetail({ params }: { params: { agentId: string } }) {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight capitalize">{params.agentId} Agent</h1>
          <p className="text-[#525252]">Agent configuration and history.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Pause Agent</Button>
          <Button>Run Now</Button>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2">
           <CardHeader><CardTitle>Recent Runs</CardTitle></CardHeader>
           <CardContent className="text-sm text-[#737373]">No recent runs found for this agent.</CardContent>
        </Card>
        <Card>
           <CardHeader><CardTitle>Capabilities</CardTitle></CardHeader>
           <CardContent className="space-y-2 text-sm text-[#525252]">
             <li>Data analysis</li>
             <li>Trend forecasting</li>
             <li>Competitor tracking</li>
           </CardContent>
        </Card>
      </div>
    </div>
  )
}
"""
write_file("app/app/agents/[agentId]/page.tsx", agent_id_tsx)

content_id_tsx = """
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function ContentDetail({ params }: { params: { id: string } }) {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Content: {params.id}</h1>
          <p className="text-[#525252]">Drafting and approval.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Reject</Button>
          <Button>Approve & Publish</Button>
        </div>
      </div>
      <Card>
        <CardHeader><CardTitle>Draft Preview</CardTitle></CardHeader>
        <CardContent>
           <div className="prose max-w-none text-sm text-[#525252]">
             <p>This is a simulated piece of content generated by an AI agent.</p>
             <p>It includes formatting, paragraphs, and insights ready for review.</p>
           </div>
        </CardContent>
      </Card>
    </div>
  )
}
"""
write_file("app/app/content/[id]/page.tsx", content_id_tsx)

campaign_id_tsx = """
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function CampaignDetail({ params }: { params: { id: string } }) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Campaign: {params.id}</h1>
      <Card>
        <CardHeader><CardTitle>Performance Overview</CardTitle></CardHeader>
        <CardContent className="text-sm text-[#737373]">
           Campaign data will appear here.
        </CardContent>
      </Card>
    </div>
  )
}
"""
write_file("app/app/campaigns/[id]/page.tsx", campaign_id_tsx)

settings_team_tsx = """
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function TeamSettings() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Team Settings</h1>
      <Card>
        <CardHeader className="flex flex-row justify-between items-center">
           <CardTitle>Members</CardTitle>
           <Button size="sm">Invite Member</Button>
        </CardHeader>
        <CardContent className="text-sm">
           <div className="flex justify-between border-b py-2">
             <span>demo@standbharat.ai</span>
             <span className="text-[#737373]">Owner</span>
           </div>
        </CardContent>
      </Card>
    </div>
  )
}
"""
write_file("app/app/settings/team/page.tsx", settings_team_tsx)

settings_billing_tsx = """
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function BillingSettings() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Billing Settings</h1>
      <Card>
        <CardHeader><CardTitle>Current Plan</CardTitle></CardHeader>
        <CardContent className="space-y-4">
           <p className="font-bold text-xl">Free Starter</p>
           <Button>Upgrade to Growth</Button>
        </CardContent>
      </Card>
    </div>
  )
}
"""
write_file("app/app/settings/billing/page.tsx", settings_billing_tsx)

print("Missing routes generated.")
