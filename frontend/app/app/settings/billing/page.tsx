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
