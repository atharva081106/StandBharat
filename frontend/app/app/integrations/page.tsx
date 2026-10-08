"use client"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useState, useEffect } from 'react'
import { useAppProvider } from '@/lib/providers'
import { ApiClient } from '@/lib/api/client'

export default function Integrations() {
  const { auth } = useAppProvider()
  const { activeWorkspace, activeBrand } = auth
  const [integrations, setIntegrations] = useState<any[]>([])
  const [connecting, setConnecting] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchIntegrations = async () => {
    if (!activeBrand) return
    try {
      const data = await ApiClient.get<any[]>('/api/integrations/')
      setIntegrations(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchIntegrations()
  }, [activeBrand])

  const handleConnect = async (id: string) => {
    setConnecting(id)
    try {
      await ApiClient.post('/api/integrations/' + id + '/connect', { "dummy_token": "mock_credential_123" })
      await fetchIntegrations()
    } catch (e) {
      console.error(e)
    } finally {
      setConnecting(null)
    }
  }

  const handleDisconnect = async (id: string) => {
    setConnecting(id)
    try {
      await ApiClient.post('/api/integrations/' + id + '/disconnect', {})
      await fetchIntegrations()
    } catch (e) {
      console.error(e)
    } finally {
      setConnecting(null)
    }
  }

  if (loading) return <div className="p-8 text-center text-[#A9A4A0]">Loading integrations...</div>

  return (
    <div className="p-8 w-full max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-[#F5F3F1]">Integration Hub</h1>
        <p className="text-[#A9A4A0]">Connect external platforms to your AI Marketing OS.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {integrations.map((integration: any) => (
          <Card key={integration.id} className="bg-[#1C1A1A] border-[#373333]">
            <CardHeader className="pb-2">
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg text-[#F5F3F1]">{integration.provider}</CardTitle>
                <Badge variant="outline" className="bg-[#242222] text-[#A9A4A0] border-[#373333]">{integration.category}</Badge>
              </div>
              <div className="text-[13px] text-[#A9A4A0] flex gap-2 pt-2">
                {integration.capabilities.map((c: string) => <span key={c} className="bg-[#2A2828] px-1.5 py-0.5 rounded text-[10px] uppercase">{c}</span>)}
              </div>
            </CardHeader>
            <CardContent>
               <div className="flex justify-between items-center mt-4 pt-4 border-t border-[#373333]">
                 <span className="text-sm font-medium">
                   {integration.status === 'CONNECTED' ? <span className="text-[#00A650]">Connected</span> : 
                    integration.status === 'COMING_SOON' ? <span className="text-[#F5A623]">Coming Soon</span> :
                    <span className="text-[#A9A4A0]">Not connected</span>}
                 </span>
                 
                 {integration.status === 'CONNECTED' ? (
                   <Button 
                     variant="outline" 
                     size="sm"
                     className="border-[#373333] hover:bg-[#8F0028] hover:text-white hover:border-[#8F0028] text-[#F5F3F1]"
                     disabled={connecting === integration.id}
                     onClick={() => handleDisconnect(integration.id)}
                   >
                     {connecting === integration.id ? 'Disconnecting...' : 'Disconnect'}
                   </Button>
                 ) : (
                   <Button 
                     variant="default" 
                     size="sm"
                     className="bg-[#F5F3F1] text-[#171515] hover:bg-white"
                     disabled={connecting === integration.id || integration.status === 'COMING_SOON'}
                     onClick={() => handleConnect(integration.id)}
                   >
                     {connecting === integration.id ? 'Connecting...' : 'Connect'}
                   </Button>
                 )}
               </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
