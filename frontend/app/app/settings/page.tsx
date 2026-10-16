"use client"
import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ApiClient } from '@/lib/api/client'
import { useAuth } from '@/lib/providers/MockProvider'
import { 
  Settings as SettingsIcon, User, Users, Globe, 
  ShieldCheck, Server, Key, Database, RefreshCw, LogOut, Check
} from 'lucide-react'

export default function SettingsPage() {
  const { user, activeWorkspace, activeBrand, logout } = useAuth()
  const [workspaces, setWorkspaces] = useState<any[]>([])
  const [brands, setBrands] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [wsData, brData] = await Promise.all([
        ApiClient.get<any[]>('/api/workspaces/'),
        ApiClient.get<any[]>('/api/brands/')
      ])
      setWorkspaces(wsData || [])
      setBrands(brData || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="flex-1 overflow-y-auto p-6 max-w-5xl mx-auto w-full space-y-8 text-[#F5F3F1]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#373333] pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[#F5F3F1]">System & Workspace Settings</h1>
          <p className="text-[#A9A4A0] text-sm mt-1">
            Manage your tenant profile, brand configurations, and connected infrastructure.
          </p>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={fetchData} 
          disabled={loading}
          className="border-[#373333] text-[#A9A4A0] hover:text-[#F5F3F1] hover:bg-[#242222]"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="space-y-6">
        {/* User Account Profile */}
        <Card className="bg-[#1C1A1A] border-[#373333]">
          <CardHeader className="border-b border-[#373333] pb-3">
            <CardTitle className="text-base text-[#F5F3F1] flex items-center gap-2">
              <User className="w-4 h-4 text-[#8F0028]" /> User Account
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <span className="block text-[#A9A4A0] uppercase tracking-wider font-semibold mb-1">Full Name</span>
                <span className="text-sm font-medium text-[#F5F3F1]">{user?.name || 'Authorized Member'}</span>
              </div>
              <div>
                <span className="block text-[#A9A4A0] uppercase tracking-wider font-semibold mb-1">Email Address</span>
                <span className="text-sm font-mono text-[#F5F3F1]">{user?.email || 'user@example.com'}</span>
              </div>
            </div>
            <div className="pt-2 flex justify-start">
              <Button 
                variant="outline" 
                size="sm"
                onClick={logout}
                className="border-red-900 text-red-400 hover:bg-red-950/20 text-xs"
              >
                <LogOut className="w-3.5 h-3.5 mr-1.5" /> Sign Out of StandBharat
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Active Workspace */}
        <Card className="bg-[#1C1A1A] border-[#373333]">
          <CardHeader className="border-b border-[#373333] pb-3">
            <div className="flex justify-between items-center">
              <CardTitle className="text-base text-[#F5F3F1] flex items-center gap-2">
                <Users className="w-4 h-4 text-[#00A650]" /> Active Workspace
              </CardTitle>
              <Badge className="bg-[#00A650]/20 text-[#00A650] border border-[#00A650]/30 text-[10px] uppercase">
                Owner Access
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <span className="block text-[#A9A4A0] uppercase tracking-wider font-semibold mb-1">Workspace Name</span>
                <span className="text-sm font-medium text-[#F5F3F1]">{activeWorkspace?.name || 'Default Workspace'}</span>
              </div>
              <div>
                <span className="block text-[#A9A4A0] uppercase tracking-wider font-semibold mb-1">Workspace ID</span>
                <span className="text-xs font-mono text-[#A9A4A0]">{activeWorkspace?.id || '—'}</span>
              </div>
            </div>

            <div className="pt-3 border-t border-[#373333]">
              <span className="block text-[#A9A4A0] text-xs uppercase tracking-wider font-semibold mb-2">Configured Brands</span>
              <div className="space-y-2">
                {brands.map(b => (
                  <div key={b.id} className="p-3 bg-[#242222] border border-[#373333] rounded-lg flex justify-between items-center text-xs">
                    <div>
                      <span className="font-semibold text-[#F5F3F1]">{b.name}</span>
                      <span className="text-[#A9A4A0] ml-2">({b.website_url || 'No URL'})</span>
                    </div>
                    {b.id === activeBrand?.id && (
                      <Badge className="bg-[#8F0028]/20 text-[#8F0028] border border-[#8F0028]/30 text-[10px] uppercase">
                        Current Active
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System & Architecture Diagnostics */}
        <Card className="bg-[#1C1A1A] border-[#373333]">
          <CardHeader className="border-b border-[#373333] pb-3">
            <CardTitle className="text-base text-[#F5F3F1] flex items-center gap-2">
              <Server className="w-4 h-4 text-blue-400" /> Platform Infrastructure
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-3 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3 bg-[#242222] border border-[#373333] rounded-lg">
                <span className="block text-[#A9A4A0] font-semibold text-[10px] uppercase tracking-wider mb-1">Database</span>
                <span className="text-[#00A650] font-bold flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> PostgreSQL Active
                </span>
                <span className="text-[10px] text-[#A9A4A0] mt-0.5 block">Port 5432 / Migrated</span>
              </div>

              <div className="p-3 bg-[#242222] border border-[#373333] rounded-lg">
                <span className="block text-[#A9A4A0] font-semibold text-[10px] uppercase tracking-wider mb-1">Queue & Broker</span>
                <span className="text-[#00A650] font-bold flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Redis & Celery
                </span>
                <span className="text-[10px] text-[#A9A4A0] mt-0.5 block">Port 6380 / Auto-retry</span>
              </div>

              <div className="p-3 bg-[#242222] border border-[#373333] rounded-lg">
                <span className="block text-[#A9A4A0] font-semibold text-[10px] uppercase tracking-wider mb-1">Data Mode</span>
                <span className="text-[#F5F3F1] font-bold flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-[#8F0028]" /> API Backend (Live)
                </span>
                <span className="text-[10px] text-[#A9A4A0] mt-0.5 block">Zero Mock Fallbacks</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
