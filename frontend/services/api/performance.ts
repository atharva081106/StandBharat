export interface PerformanceSnapshot {
  id: string
  publication_id?: string
  channel: string
  captured_at: string
  impressions?: number
  reach?: number
  engagements?: number
  likes?: number
  comments?: number
  shares?: number
  clicks?: number
  video_views?: number
  saves?: number
  engagement_rate?: number
  source_status: string
}

export interface PerformanceSummaryResponse {
  status: 'AVAILABLE' | 'NOT_AVAILABLE' | 'PARTIAL'
  reason?: string
  period: {
    start: string
    end: string
  }
  channels: string[]
  metrics: Record<string, any>
  top_publications: PerformanceSnapshot[]
  trends: any[]
}

export interface PerformanceProvider {
  getSummary(workspaceId: string, brandId: string): Promise<PerformanceSummaryResponse>
}

export class ApiPerformanceProvider implements PerformanceProvider {
  async getSummary(workspaceId: string, brandId: string): Promise<PerformanceSummaryResponse> {
    const token = localStorage.getItem('standbharat_token')
    const res = await fetch(`/api/performance/${workspaceId}/${brandId}/summary`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!res.ok) {
      throw new Error('Failed to fetch performance summary')
    }
    
    return res.json()
  }
}

export class MockPerformanceProvider implements PerformanceProvider {
  async getSummary(workspaceId: string, brandId: string): Promise<PerformanceSummaryResponse> {
    // Return controlled development data
    return {
      status: 'AVAILABLE',
      period: {
        start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        end: new Date().toISOString()
      },
      channels: ['linkedin'],
      metrics: {
        total_impressions: 12450,
        total_engagements: 856
      },
      top_publications: [
        {
          id: 'mock-1',
          channel: 'linkedin',
          captured_at: new Date().toISOString(),
          impressions: 4500,
          engagements: 340,
          engagement_rate: 0.075,
          source_status: 'SUCCESS'
        }
      ],
      trends: [
        { name: 'Engagement Trend', type: 'ENGAGEMENT_TREND', confidence: 'HIGH', interpretation: 'Educational posts are outperforming promotional.' }
      ]
    }
  }
}

// Factory
export const getPerformanceProvider = (useMock = false): PerformanceProvider => {
  return useMock ? new MockPerformanceProvider() : new ApiPerformanceProvider()
}
