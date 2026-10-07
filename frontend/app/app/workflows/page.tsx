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
