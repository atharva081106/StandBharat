"use client"
import { useState, useEffect } from 'react'
import { useBrandBrain } from '@/lib/providers/MockProvider'
import { Loader2 } from 'lucide-react'

export function BrandVoicePanel() {
  const { brandBrain, loading } = useBrandBrain()
  const [voice, setVoice] = useState<any>(null)

  useEffect(() => {
    if (brandBrain?.voice) {
      setVoice(brandBrain.voice)
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
        <h2 className="text-[20px] font-bold text-[#F5F3F1] mb-1">Brand Voice</h2>
        <p className="text-[13px] text-[#A9A4A0]">
          Configure the tone, language, and guidelines for your brand.
        </p>
      </div>
      
      <div className="space-y-6">
        <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
          <h3 className="text-sm font-bold text-[#F5F3F1] mb-4">Tone & Persona Guidelines</h3>
          {voice ? (
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="text-[11px] font-bold text-[#A9A4A0] uppercase mb-1 block">Archetype</label>
                <div className="bg-[#1C1A1A] border border-[#373333] p-2.5 rounded text-[13px] text-white">{voice.personality || 'Not set'}</div>
              </div>
              <div>
                <label className="text-[11px] font-bold text-[#A9A4A0] uppercase mb-1 block">Formality</label>
                <div className="bg-[#1C1A1A] border border-[#373333] p-2.5 rounded text-[13px] text-white">{voice.formality || 'Not set'}</div>
              </div>
              <div className="col-span-2">
                <label className="text-[11px] font-bold text-[#A9A4A0] uppercase mb-1 block">Tone</label>
                <div className="bg-[#1C1A1A] border border-[#373333] p-2.5 rounded text-[13px] text-white">{voice.tone || 'Not set'}</div>
              </div>
            </div>
          ) : (
            <p className="text-[12px] text-[#A9A4A0] italic">Brand voice not configured yet.</p>
          )}
        </div>
      </div>
    </div>
  )
}
