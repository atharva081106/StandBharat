"use client"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { mockApprovals } from '@/lib/mock/data'
import { useState } from 'react'

export default function Approvals() {
  const [items, setItems] = useState(mockApprovals)

  const handleAction = (id: string, action: 'approve' | 'reject') => {
    setItems(prev => prev.filter(a => a.id !== id))
  }
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Approvals</h1>
        <p className="text-[#525252]">Manage your pending and past approvals.</p>
      </div>
      
      <div className="space-y-4">
        {items.map(app => (
          <Card key={app.id}>
            <CardContent className="flex items-center justify-between p-6">
               <div>
                  <h3 className="font-medium text-lg">{app.title}</h3>
                  <div className="flex gap-4 mt-2 text-sm text-[#737373]">
                    <span>Agent: {app.agent}</span>
                    <span>Risk: <Badge variant={app.risk === 'HIGH' ? 'danger' : 'secondary'}>{app.risk}</Badge></span>
                    <span>Requested: {app.requested}</span>
                  </div>
               </div>
               <div className="flex gap-2">
                 <Button variant="outline" onClick={() => handleAction(app.id, 'reject')}>Reject</Button>
                 <Button onClick={() => handleAction(app.id, 'approve')}>Approve</Button>
               </div>
            </CardContent>
          </Card>
        ))}
        {items.length === 0 && (
          <div className="p-12 text-center border border-[#E5E5E5] bg-white rounded-xl text-[#737373]">
             No pending approvals.
          </div>
        )}
      </div>
    </div>
  )
}
