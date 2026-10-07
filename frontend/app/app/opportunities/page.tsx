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
