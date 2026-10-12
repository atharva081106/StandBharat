"use client"
import { useAppProvider } from '@/lib/providers'
import { FileText, Loader2 } from 'lucide-react'

const typeMap: Record<string, string> = {
  'Product Information': 'PRODUCT_INFORMATION',
  'Competitor Analysis': 'COMPETITOR_ANALYSIS',
  'Brand Voice Guide': 'BRAND_VOICE',
  'Growth Playbook': 'GROWTH_PLAYBOOK'
}

export function StrategyDocumentPanel({ documentName }: { documentName: string }) {
  const { auth: { activeBrand }, brandBrain } = useAppProvider()
  
  // Actually, we could fetch context or pass it. 
  // For simplicity, we just use the context from the provider if we can, but brandBrain.getContext() is async.
  // Wait, let's use the same pattern as others: fetch it on mount
  const [loading, setLoading] = React.useState(true)
  const [doc, setDoc] = React.useState<any>(null)

  React.useEffect(() => {
    async function fetchDoc() {
      if (!activeBrand?.id) return
      setLoading(true)
      try {
        const ctx = await brandBrain.getContext()
        const expectedType = typeMap[documentName]
        const found = (ctx.strategy_documents || []).find((d: any) => d.type === expectedType)
        setDoc(found)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchDoc()
  }, [activeBrand, documentName])

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-[#A9A4A0] animate-spin" />
      </div>
    )
  }

  if (!doc) {
    return (
      <div className="flex-1 flex flex-col h-full bg-[#1C1A1A] p-8 overflow-y-auto custom-scrollbar">
        <div className="mb-6">
          <h2 className="text-[20px] font-bold text-[#F5F3F1] mb-1">{documentName}</h2>
          <p className="text-[13px] text-[#A9A4A0]">
            This document has not been generated yet. It will be created automatically once sufficient research is completed.
          </p>
        </div>
      </div>
    )
  }

  const content = doc.content || {}

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-6 bg-[#1C1A1A]">
      <div className="max-w-3xl space-y-8 pb-10">
        
        {/* Header */}
        <div>
          <h2 className="text-[18px] font-bold text-[#F5F3F1] flex items-center gap-2">
            <FileText className="w-5 h-5 text-[#8F0028]" />
            {content.title || documentName}
          </h2>
          {content.executive_summary && (
            <p className="text-[13px] text-[#A9A4A0] mt-2 leading-relaxed">
              {content.executive_summary}
            </p>
          )}
        </div>

        {doc.status === 'NOT_CONFIGURED' && (
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/50 rounded-lg text-yellow-500 text-[13px]">
            AI is not configured.
          </div>
        )}

        <div className="space-y-8">
          {(content.sections || []).map((section: any, idx: number) => (
            <div key={idx} className="space-y-3">
              <h3 className="text-[15px] font-bold text-[#F5F3F1] border-b border-[#373333] pb-2">
                {section.heading}
              </h3>
              <div className="text-[13px] text-[#A9A4A0] leading-relaxed whitespace-pre-wrap">
                {section.content}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

import React from 'react'
