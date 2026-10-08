"use client"
import { useState, useEffect } from 'react'
import { useBrandBrain } from '@/lib/providers/MockProvider'
import { Plus, Loader2, ExternalLink } from 'lucide-react'

export function CompetitorsPanel() {
  const { brandBrain, loading } = useBrandBrain()
  const [competitors, setCompetitors] = useState<any[]>([])

  useEffect(() => {
    const isApi = process.env.NEXT_PUBLIC_DATA_MODE === 'api'
    let initialCompetitors = brandBrain?.competitors || [];
    if (initialCompetitors.length === 0 && !isApi) {
      try {
        const obData = localStorage.getItem('onboardingData');
        if (obData) {
          const parsed = JSON.parse(obData);
          if (parsed.competitors && parsed.competitors.length > 0) {
            initialCompetitors = parsed.competitors.map((c: string, index: number) => ({
              id: `onboarding-competitor-${index}`,
              name: c,
              positioning: 'To be analyzed'
            }))
          }
        }
      } catch(e) {}
    }
    setCompetitors(initialCompetitors);
  }, [brandBrain])

  if (loading) {
    return (
      <div className="flex-1 flex flex-col h-full bg-[#1C1A1A] p-8 overflow-y-auto custom-scrollbar justify-center items-center">
        <Loader2 className="w-6 h-6 text-[#A9A4A0] animate-spin" />
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#1C1A1A] p-8 overflow-y-auto custom-scrollbar">
      <div className="mb-6">
        <h2 className="text-[20px] font-bold text-[#F5F3F1] mb-1">Competitors</h2>
        <p className="text-[13px] text-[#A9A4A0]">
          Track your competitive landscape. Used by the Competitor Agent and AI CMO.
        </p>
      </div>

      <div className="space-y-6">
        <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
          <h3 className="text-sm font-bold text-[#F5F3F1] mb-4">Tracked Competitors</h3>

          <div className="space-y-3">
            {competitors.length === 0 ? (
              <p className="text-[12px] text-[#A9A4A0] italic">No competitors tracked yet.</p>
            ) : (
              competitors.map((competitor: any, index: number) => (
                <div key={competitor.id || index} className="bg-[#1C1A1A] border border-[#373333] p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-[13px] font-bold text-white">{competitor.name}</h4>
                    {competitor.website && (
                      <a
                        href={competitor.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[#A9A4A0] hover:text-[#F5F3F1] transition-colors"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    )}
                  </div>
                  {competitor.positioning && (
                    <p className="text-[12px] text-[#A9A4A0]">{competitor.positioning}</p>
                  )}
                  {competitor.strengths && (
                    <p className="text-[11px] text-[#A9A4A0] mt-1">
                      <span className="text-[#00A650] font-semibold">Strengths: </span>
                      {competitor.strengths}
                    </p>
                  )}
                  {competitor.weaknesses && (
                    <p className="text-[11px] text-[#A9A4A0] mt-1">
                      <span className="text-[#FF7A85] font-semibold">Weaknesses: </span>
                      {competitor.weaknesses}
                    </p>
                  )}
                </div>
              ))
            )}
          </div>

          <button className="mt-4 text-[12px] font-semibold text-[#F5F3F1] border border-[#373333] px-3 py-1.5 rounded flex items-center gap-2 hover:bg-[#373333] transition-colors">
            <Plus className="w-3.5 h-3.5" /> Add Competitor
          </button>
        </div>
      </div>
    </div>
  )
}
