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
