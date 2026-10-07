import os
from pathlib import Path

BASE_DIR = Path("frontend")

def write_file(path, content):
    full_path = BASE_DIR / path
    os.makedirs(full_path.parent, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# --- app/app/agents/page.tsx ---
agents_tsx = """
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { mockAgents } from '@/lib/mock/data'
import { Bot } from 'lucide-react'

export default function Agents() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">AI Agents</h1>
        <p className="text-[#525252]">Your autonomous marketing team.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {mockAgents.map((agent) => (
          <Card key={agent.id}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Bot className="h-5 w-5 text-orange-500" />
                {agent.name}
              </CardTitle>
              <Badge variant={agent.status === 'ACTIVE' ? 'success' : agent.status === 'WAITING' ? 'warning' : 'secondary'}>
                {agent.status}
              </Badge>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-[#525252] mb-4">{agent.description}</p>
              <div className="flex justify-between text-xs text-[#737373]">
                <span>Last run: 2h ago</span>
                <span className="text-orange-500 cursor-pointer hover:underline">View Agent →</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
"""
write_file("app/app/agents/page.tsx", agents_tsx)

# --- app/app/workflows/page.tsx ---
workflows_tsx = """
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function Workflows() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Workflows</h1>
        <p className="text-[#525252]">Multi-agent sequences and marketing funnels.</p>
      </div>
      
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Weekly Growth Optimization</CardTitle>
          </CardHeader>
          <CardContent>
             <div className="flex items-center gap-2 overflow-x-auto pb-4">
               <div className="px-4 py-2 bg-green-50 border border-green-200 text-green-700 rounded-md text-sm font-medium whitespace-nowrap">Analytics</div>
               <span className="text-[#E5E5E5]">→</span>
               <div className="px-4 py-2 bg-green-50 border border-green-200 text-green-700 rounded-md text-sm font-medium whitespace-nowrap">SEO</div>
               <span className="text-[#E5E5E5]">→</span>
               <div className="px-4 py-2 bg-amber-50 border border-amber-200 text-amber-700 rounded-md text-sm font-medium whitespace-nowrap">Growth (Running)</div>
               <span className="text-[#E5E5E5]">→</span>
               <div className="px-4 py-2 bg-gray-50 border border-[#E5E5E5] text-[#737373] rounded-md text-sm font-medium whitespace-nowrap">Writer</div>
             </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
"""
write_file("app/app/workflows/page.tsx", workflows_tsx)

# --- app/app/opportunities/page.tsx ---
opps_tsx = """
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { mockOpportunities } from '@/lib/mock/data'

export default function Opportunities() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Opportunities</h1>
        <p className="text-[#525252]">Prioritized marketing actions identified by AI.</p>
      </div>
      
      <div className="space-y-4">
        {mockOpportunities.map(opp => (
          <Card key={opp.id}>
            <CardContent className="flex flex-col md:flex-row items-start md:items-center justify-between p-6 gap-4">
              <div>
                <h3 className="font-medium text-lg">{opp.title}</h3>
                <div className="flex gap-4 mt-2 text-sm">
                  <span>Impact: <span className="font-medium text-orange-600">{opp.impact}</span></span>
                  <span>Confidence: <span className="font-medium">{opp.confidence}</span></span>
                  <span>Priority Score: <span className="font-medium text-orange-500">{opp.priority}</span></span>
                </div>
              </div>
              <div className="flex gap-2 w-full md:w-auto">
                 <Button variant="outline">Dismiss</Button>
                 <Button>Execute Action</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
"""
write_file("app/app/opportunities/page.tsx", opps_tsx)

# --- app/app/content/page.tsx ---
content_tsx = """
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { mockContent } from '@/lib/mock/data'

export default function Content() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Content Studio</h1>
          <p className="text-[#525252]">All AI-generated and human marketing content.</p>
        </div>
        <Button>+ New Content</Button>
      </div>
      
      <div className="bg-white border border-[#E5E5E5] rounded-xl overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="bg-[#FAFAF8] text-[#525252] border-b border-[#E5E5E5]">
            <tr>
              <th className="px-6 py-4 font-medium">Title</th>
              <th className="px-6 py-4 font-medium">Type</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">Author</th>
              <th className="px-6 py-4 font-medium">Updated</th>
            </tr>
          </thead>
          <tbody>
            {mockContent.map((item, i) => (
              <tr key={item.id} className={i !== mockContent.length - 1 ? 'border-b border-[#E5E5E5]' : ''}>
                <td className="px-6 py-4 font-medium">{item.title}</td>
                <td className="px-6 py-4">{item.type}</td>
                <td className="px-6 py-4">
                  <Badge variant={item.status === 'PUBLISHED' ? 'success' : 'secondary'}>{item.status}</Badge>
                </td>
                <td className="px-6 py-4">{item.author}</td>
                <td className="px-6 py-4 text-[#737373]">{item.updated}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
"""
write_file("app/app/content/page.tsx", content_tsx)

# --- Generating placeholders for the rest of the generic routes ---
generic_pages = [
    "calendar", "campaigns", "analytics", "revenue", "competitors", "approvals", "integrations", "settings"
]

for page in generic_pages:
    content = f"""
export default function {page.title()}() {{
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight capitalize">{page}</h1>
        <p className="text-[#525252]">Manage your {page} settings and details.</p>
      </div>
      <div className="p-12 text-center border border-[#E5E5E5] bg-white rounded-xl text-[#737373]">
         This module is connected to mock data. Details will populate once fully integrated.
      </div>
    </div>
  )
}}
"""
    write_file(f"app/app/{page}/page.tsx", content)

print("Remaining App routes generated.")
