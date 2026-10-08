"use client"
import { useState, useEffect } from 'react'
import { useBrandBrain } from '@/lib/providers/MockProvider'
import { Plus, Loader2 } from 'lucide-react'

export function AudiencePanel() {
  const { brandBrain, loading } = useBrandBrain()
  const [audiences, setAudiences] = useState<any[]>([])

  useEffect(() => {
    if (brandBrain?.audiences) {
      setAudiences(brandBrain.audiences)
    }
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
        <h2 className="text-[20px] font-bold text-[#F5F3F1] mb-1">Audience</h2>
        <p className="text-[13px] text-[#A9A4A0]">
          Define who you are targeting and their core pain points.
        </p>
      </div>
      
      <div className="space-y-6">
        <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
          <h3 className="text-sm font-bold text-[#F5F3F1] mb-4">Target Personas</h3>
          
          <div className="space-y-4">
            {audiences.length === 0 ? (
              <p className="text-[12px] text-[#A9A4A0] italic">No audiences defined yet.</p>
            ) : (
              audiences.map((audience: any, index: number) => (
                <div key={audience.id || index} className={`flex justify-between items-start ${index !== audiences.length - 1 ? 'border-b border-[#373333] pb-4' : ''}`}>
                  <div>
                    <h4 className="text-[13px] font-bold text-white mb-1">{audience.name}</h4>
                    <p className="text-[12px] text-[#A9A4A0]">{audience.demographics}</p>
                    <p className="text-[12px] text-[#A9A4A0] mt-2 max-w-lg">Pain points: {audience.pain_points}</p>
                  </div>
                  <button className="text-[11px] font-semibold text-[#8F0028] bg-[#8F0028]/10 px-2 py-1 rounded">Edit</button>
                </div>
              ))
            )}
          </div>
          
          <button className="mt-4 text-[12px] font-semibold text-[#F5F3F1] border border-[#373333] px-3 py-1.5 rounded flex items-center gap-2 hover:bg-[#373333] transition-colors">
            <Plus className="w-3.5 h-3.5" /> Add Persona
          </button>
        </div>
      </div>
    </div>
  )
}
