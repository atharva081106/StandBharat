"use client"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useState, useEffect } from 'react'
import { useAppProvider } from '@/lib/providers'
import { ApiClient } from '@/lib/api/client'
import { Input } from '@/components/ui/input'

export default function Integrations() {
  const { auth } = useAppProvider()
  const { activeWorkspace, activeBrand } = auth
  const [integrations, setIntegrations] = useState<any[]>([])
  const [connecting, setConnecting] = useState<string | null>(null)
  const [wpForm, setWpForm] = useState({ site_url: '', username: '', app_password: '' })
  const [wpError, setWpError] = useState<string | null>(null)
  const [authError, setAuthError] = useState<{id: string, message: string} | null>(null)
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
    if (id === 'wordpress' && connecting !== 'wordpress') {
      setConnecting('wordpress')
      setWpError(null)
      return
    }

    setConnecting(id)
    setAuthError(null)
    try {
      if (id === 'gsc' || id === 'ga4' || id === 'linkedin' || id === 'twitter_x' || id === 'reddit') {
        const data = await ApiClient.get<any>(`/api/integrations/${id}/oauth/login`)
        if (data && data.authorization_url) {
          window.location.href = data.authorization_url
          return
        }
      } else if (id === 'wordpress') {
        await ApiClient.post('/api/integrations/wordpress/connect', wpForm)
        setWpForm({ site_url: '', username: '', app_password: '' })
      } else {
        throw new Error(`${id.toUpperCase()} connection requires valid credentials. Mock connection is disabled.`)
      }
      await fetchIntegrations()
      setConnecting(null)
    } catch (e: any) {
      console.error(e)
      if (id === 'wordpress') {
        setWpError(e.message || "Failed to connect to WordPress")
      } else {
        setAuthError({id, message: e.message || "Configuration missing or authorization failed."})
        setConnecting(null)
      }
    }
  }

  const cancelConnect = () => {
    setConnecting(null)
    setWpError(null)
  }

  const handleSync = async (id: string) => {
    try {
      await ApiClient.post('/api/integrations/' + id + '/sync', {})
      await fetchIntegrations()
    } catch (e) {
      console.error(e)
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
                    integration.status === 'SYNCING' ? <span className="text-[#3B82F6]">Syncing...</span> :
                    integration.status === 'ERROR' ? <span className="text-[#EF4444]">Error</span> :
                    integration.status === 'COMING_SOON' ? <span className="text-[#F5A623]">Coming Soon</span> :
                    <span className="text-[#A9A4A0]">Not connected</span>}
                 </span>
                 
                 {integration.status === 'CONNECTED' || integration.status === 'ERROR' || integration.status === 'SYNCING' ? (
                   <div className="flex gap-2">
                     <Button 
                       variant="outline" 
                       size="sm"
                       className="border-[#373333] hover:bg-[#373333] text-[#F5F3F1]"
                       disabled={integration.status === 'SYNCING'}
                       onClick={() => handleSync(integration.id)}
                     >
                       Sync
                     </Button>
                     <Button 
                       variant="outline" 
                       size="sm"
                       className="border-[#373333] hover:bg-[#8F0028] hover:text-white hover:border-[#8F0028] text-[#F5F3F1]"
                       disabled={connecting === integration.id}
                       onClick={() => handleDisconnect(integration.id)}
                     >
                       {connecting === integration.id ? 'Disconnecting...' : 'Disconnect'}
                     </Button>
                   </div>
                 ) : connecting === integration.id && integration.id === 'wordpress' ? (
                   null
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

               {authError && authError.id === integration.id && (
                 <div className="mt-3 p-3 bg-[#373333] rounded text-xs text-[#EF4444]">
                   <strong>Action Required:</strong> {authError.message}
                 </div>
               )}

               {connecting === integration.id && integration.id === 'wordpress' && (
                 <div className="mt-4 pt-4 border-t border-[#373333] space-y-3">
                   {wpError && <div className="text-[#EF4444] text-xs">{wpError}</div>}
                   <Input 
                     placeholder="Site URL (e.g. https://example.com)" 
                     value={wpForm.site_url}
                     onChange={e => setWpForm({...wpForm, site_url: e.target.value})}
                     className="bg-[#242222] border-[#373333] text-sm"
                   />
                   <Input 
                     placeholder="Username" 
                     value={wpForm.username}
                     onChange={e => setWpForm({...wpForm, username: e.target.value})}
                     className="bg-[#242222] border-[#373333] text-sm"
                   />
                   <Input 
                     placeholder="Application Password" 
                     type="password"
                     value={wpForm.app_password}
                     onChange={e => setWpForm({...wpForm, app_password: e.target.value})}
                     className="bg-[#242222] border-[#373333] text-sm"
                   />
                   <div className="flex justify-end gap-2 pt-2">
                     <Button variant="outline" size="sm" onClick={cancelConnect} className="border-[#373333] text-[#A9A4A0]">Cancel</Button>
                     <Button variant="default" size="sm" onClick={() => handleConnect(integration.id)} className="bg-[#F5F3F1] text-[#171515]">Submit</Button>
                   </div>
                 </div>
               )}

               {(integration.last_sync_at || integration.last_error) && integration.status !== 'NOT_CONNECTED' && integration.status !== 'COMING_SOON' && (
                 <div className="mt-2 text-xs text-[#A9A4A0]">
                   {integration.last_sync_at && <div>Last sync: {new Date(integration.last_sync_at).toLocaleString()}</div>}
                   {integration.last_error && <div className="text-[#EF4444] mt-1">Error: {integration.last_error}</div>}
                 </div>
               )}
             </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
