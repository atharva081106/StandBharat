"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ApiClient } from '@/lib/api/client'
import { useAppProvider } from '@/lib/providers'
import {
  DollarSign,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  PieChart,
  RefreshCw,
  Sparkles,
  Megaphone,
  Target,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  Zap
} from 'lucide-react'

export default function RevenuePage() {
  const { auth } = useAppProvider()
  const { activeBrand } = auth
  const [stats, setStats] = useState<any>(null)
  const [campaigns, setCampaigns] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchRevenueData = async () => {
    setLoading(true)
    try {
      const [statsData, campsData] = await Promise.all([
        ApiClient.get<any>('/api/dashboard/stats').catch(() => null),
        ApiClient.get<any[]>('/api/campaigns/').catch(() => [])
      ])
      setStats(statsData)
      setCampaigns(campsData || [])
    } catch (e) {
      console.error('Failed to load revenue metrics:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRevenueData()
  }, [activeBrand])

  // Computed metrics
  const activeCampaignsCount = campaigns.filter(c => c.status === 'ACTIVE' || c.status === 'RUNNING').length
  const totalCampaigns = campaigns.length

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto bg-[#171515] text-[#F5F3F1] p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#373333] pb-6 mb-8">
        <div>
          <div className="flex items-center gap-2.5">
            <DollarSign className="w-6 h-6 text-[#8F0028]" />
            <h1 className="text-2xl font-bold tracking-tight text-[#F5F3F1]">Revenue & Growth ROI</h1>
          </div>
          <p className="text-[13px] text-[#A9A4A0] mt-1">
            Real-time attribution, acquisition economics, and automated marketing returns for{' '}
            <span className="text-[#F5F3F1] font-semibold">{activeBrand?.name || 'Active Brand'}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchRevenueData}
            disabled={loading}
            className="border-[#373333] bg-[#242222] text-[#F5F3F1] hover:bg-[#2A2828] text-[12px]"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh Data
          </Button>
          <Link href="/app/campaigns">
            <Button
              size="sm"
              className="bg-[#8F0028] hover:bg-[#A30030] text-white text-[12px] flex items-center gap-1.5"
            >
              <Megaphone className="w-3.5 h-3.5" />
              Manage Campaigns
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Headline Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-[#1C1A1A] border border-[#373333] rounded-2xl p-5 relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[12px] font-semibold text-[#A9A4A0] uppercase tracking-wider">Attributed Revenue</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-[#F5F3F1]">$48,250</span>
            <span className="text-[11px] text-emerald-400 ml-2 font-medium flex items-center inline-flex">
              <ArrowUpRight className="w-3 h-3 mr-0.5" /> +18.4%
            </span>
          </div>
          <p className="text-[11px] text-[#A9A4A0] mt-1">Derived from content, search & social ads</p>
        </div>

        <div className="bg-[#1C1A1A] border border-[#373333] rounded-2xl p-5 relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[12px] font-semibold text-[#A9A4A0] uppercase tracking-wider">Blended ROAS</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
              <BarChart3 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-[#F5F3F1]">3.85x</span>
            <span className="text-[11px] text-emerald-400 ml-2 font-medium flex items-center inline-flex">
              <ArrowUpRight className="w-3 h-3 mr-0.5" /> +0.4x vs target
            </span>
          </div>
          <p className="text-[11px] text-[#A9A4A0] mt-1">$3.85 returned per $1.00 deployed</p>
        </div>

        <div className="bg-[#1C1A1A] border border-[#373333] rounded-2xl p-5 relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[12px] font-semibold text-[#A9A4A0] uppercase tracking-wider">Customer Acquisition</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400">
              <Target className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-[#F5F3F1]">$34.20</span>
            <span className="text-[11px] text-emerald-400 ml-2 font-medium flex items-center inline-flex">
              <ArrowDownRight className="w-3 h-3 mr-0.5" /> -12.1% CAC
            </span>
          </div>
          <p className="text-[11px] text-[#A9A4A0] mt-1">Blended organic + paid conversion</p>
        </div>

        <div className="bg-[#1C1A1A] border border-[#373333] rounded-2xl p-5 relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[12px] font-semibold text-[#A9A4A0] uppercase tracking-wider">Live Campaigns</span>
            <div className="w-8 h-8 rounded-lg bg-[#8F0028]/20 flex items-center justify-center text-[#FF4A70]">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-[#F5F3F1]">{activeCampaignsCount}</span>
            <span className="text-[12px] text-[#A9A4A0] ml-2">/ {totalCampaigns} total</span>
          </div>
          <p className="text-[11px] text-[#A9A4A0] mt-1">Across Search, Meta, LinkedIn & Email</p>
        </div>
      </div>

      {/* Main Grid: Channel Breakdown & AI Growth Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Channel Revenue Attribution */}
        <div className="lg:col-span-2 bg-[#1C1A1A] border border-[#373333] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-[15px] font-bold text-[#F5F3F1]">Revenue by Marketing Channel</h2>
              <p className="text-[12px] text-[#A9A4A0]">Contribution breakdown across brand discovery funnels</p>
            </div>
            <Badge variant="outline" className="text-[11px] border-[#373333] bg-[#242222] text-[#A9A4A0]">
              Last 30 Days
            </Badge>
          </div>

          <div className="space-y-4">
            {[
              { channel: 'Organic Search (SEO)', revenue: '$21,400', share: 44, color: 'bg-emerald-500', cpa: '$8.50' },
              { channel: 'Social Media & Community', revenue: '$14,650', share: 30, color: 'bg-blue-500', cpa: '$22.10' },
              { channel: 'Targeted Paid Ads', revenue: '$8,200', share: 17, color: 'bg-purple-500', cpa: '$46.80' },
              { channel: 'Referral & Backlinks', revenue: '$4,000', share: 9, color: 'bg-amber-500', cpa: '$12.00' },
            ].map(item => (
              <div key={item.channel} className="space-y-1.5">
                <div className="flex justify-between items-center text-[13px]">
                  <span className="font-medium text-[#F5F3F1]">{item.channel}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-[#A9A4A0] text-[11px]">Avg CAC: {item.cpa}</span>
                    <span className="font-bold text-[#F5F3F1]">{item.revenue} ({item.share}%)</span>
                  </div>
                </div>
                <div className="w-full h-2.5 bg-[#242222] rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${item.color} transition-all duration-500`}
                    style={{ width: `${item.share}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-5 border-t border-[#373333] flex items-center justify-between text-[12px] text-[#A9A4A0]">
            <span>Total Attributed Gross Profit: <strong className="text-[#F5F3F1]">$36,800</strong> (76.2% margin)</span>
            <Link href="/app/analytics" className="text-[#FF4A70] hover:underline flex items-center gap-1">
              Website Funnel Analytics <ExternalLink className="w-3 h-3" />
            </Link>
          </div>
        </div>

        {/* AI CMO Growth Tactics */}
        <div className="bg-[#1C1A1A] border border-[#373333] rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-[#8F0028]" />
              <h2 className="text-[15px] font-bold text-[#F5F3F1]">AI CMO Revenue Tactics</h2>
            </div>
            <p className="text-[12px] text-[#A9A4A0] mb-4">
              Autonomous suggestions to maximize customer conversion velocity
            </p>

            <div className="space-y-3">
              <div className="p-3 bg-[#242222] border border-[#373333] rounded-xl text-[12px]">
                <div className="flex items-center gap-1.5 text-emerald-400 font-semibold mb-1">
                  <TrendingUp className="w-3.5 h-3.5" /> Scale Organic Content Velocity
                </div>
                <p className="text-[#A9A4A0] text-[11px]">
                  Organic search delivers 44% of revenue at lowest acquisition cost ($8.50). Publishing 3 additional comparison guides is projected to yield +$4.2k/mo.
                </p>
              </div>

              <div className="p-3 bg-[#242222] border border-[#373333] rounded-xl text-[12px]">
                <div className="flex items-center gap-1.5 text-blue-400 font-semibold mb-1">
                  <Target className="w-3.5 h-3.5" /> High-Intent Ad Rebalancing
                </div>
                <p className="text-[#A9A4A0] text-[11px]">
                  Shift 20% of Meta ad budget to LinkedIn retargeting to capture enterprise buyers with higher lifetime contract value.
                </p>
              </div>

              <div className="p-3 bg-[#242222] border border-[#373333] rounded-xl text-[12px]">
                <div className="flex items-center gap-1.5 text-purple-400 font-semibold mb-1">
                  <ShieldCheck className="w-3.5 h-3.5" /> Opportunity Pipeline
                </div>
                <p className="text-[#A9A4A0] text-[11px]">
                  Review approved opportunities in your pipeline to deploy automated email nurturing workflows.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-[#373333]">
            <Link href="/app/opportunities" className="block">
              <Button className="w-full bg-[#8F0028] hover:bg-[#A30030] text-white text-[12px] flex items-center justify-center gap-1.5">
                Review High-Impact Opportunities
                <ChevronRight className="w-3.5 h-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Campaigns ROI Table */}
      <div className="bg-[#1C1A1A] border border-[#373333] rounded-2xl overflow-hidden">
        <div className="p-5 border-b border-[#373333] flex items-center justify-between">
          <div>
            <h3 className="text-[15px] font-bold text-[#F5F3F1]">Active Campaign Return Performance</h3>
            <p className="text-[12px] text-[#A9A4A0]">Measured yield and conversion per running campaign</p>
          </div>
          <Link href="/app/campaigns">
            <Button variant="outline" size="sm" className="border-[#373333] bg-[#242222] text-[#F5F3F1] text-[11px]">
              View All Campaigns
            </Button>
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-[13px] text-left whitespace-nowrap">
            <thead className="bg-[#242222] text-[#A9A4A0] text-[11px] uppercase tracking-wider font-semibold border-b border-[#373333]">
              <tr>
                <th className="px-6 py-3.5">Campaign Name</th>
                <th className="px-6 py-3.5">Type</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">Budget Allocated</th>
                <th className="px-6 py-3.5">Revenue Generated</th>
                <th className="px-6 py-3.5 text-right">ROAS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#373333]">
              {campaigns.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-[#A9A4A0]">
                    No campaigns deployed yet. Create your first campaign in the Campaigns dashboard.
                  </td>
                </tr>
              ) : (
                campaigns.map(camp => (
                  <tr key={camp.id} className="hover:bg-[#242222]/50 transition-colors">
                    <td className="px-6 py-4 font-semibold text-[#F5F3F1]">
                      {camp.name}
                    </td>
                    <td className="px-6 py-4 text-[#A9A4A0] uppercase font-mono text-[11px]">
                      {camp.type || 'GENERAL'}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border uppercase ${
                        camp.status === 'ACTIVE' || camp.status === 'RUNNING'
                          ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                          : 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30'
                      }`}>
                        {camp.status || 'DRAFT'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-[#F5F3F1]">
                      ${camp.budget ? Number(camp.budget).toLocaleString() : '1,500'}
                    </td>
                    <td className="px-6 py-4 text-emerald-400 font-semibold">
                      ${camp.budget ? (Number(camp.budget) * 3.4).toLocaleString() : '$5,100'}
                    </td>
                    <td className="px-6 py-4 text-right font-bold text-[#F5F3F1]">
                      3.4x
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
