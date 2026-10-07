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
