"use client"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useState } from 'react'

export default function Integrations() {
  const [connections, setConnections] = useState<Record<string, boolean>>({})
  const [connecting, setConnecting] = useState<string | null>(null)

  const handleConnect = (id: string) => {
    setConnecting(id)
    setTimeout(() => {
      setConnections(prev => ({ ...prev, [id]: true }))
      setConnecting(null)
    }, 1500)
  }
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Integrations</h1>
        <p className="text-[#525252]">Connect external platforms to your AI Marketing OS.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { id: 'ga', name: 'Google Analytics', category: 'Analytics' },
          { id: 'gsc', name: 'Google Search Console', category: 'SEO' },
          { id: 'linkedin', name: 'LinkedIn', category: 'Social' },
          { id: 'x', name: 'X (Twitter)', category: 'Social' },
          { id: 'github', name: 'GitHub', category: 'Development' }
        ].map(integration => (
          <Card key={integration.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg">{integration.name}</CardTitle>
                <Badge variant="outline">{integration.category}</Badge>
              </div>
            </CardHeader>
            <CardContent>
               <div className="flex justify-between items-center mt-4">
                 <span className="text-sm font-medium text-[#737373]">
                   {connections[integration.id] ? <span className="text-green-600">Connected</span> : 'Not connected'}
                 </span>
                 <Button 
                   variant={connections[integration.id] ? "outline" : "default"} 
                   size="sm"
                   disabled={connecting === integration.id || connections[integration.id]}
                   onClick={() => handleConnect(integration.id)}
                 >
                   {connecting === integration.id ? 'Connecting...' : connections[integration.id] ? 'Manage' : 'Connect'}
                 </Button>
               </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
