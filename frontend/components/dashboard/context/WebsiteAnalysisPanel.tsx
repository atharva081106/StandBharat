import { useState, useEffect } from 'react'
import { useWebsiteAnalysis } from '@/lib/providers/WebsiteAnalysisProvider'
import { Globe, RefreshCw, AlertCircle, CheckCircle2, ChevronRight, Lock } from 'lucide-react'

export function WebsiteAnalysisPanel() {
  const { analysis, loading, error, triggerAnalysis } = useWebsiteAnalysis()
  const [isTriggering, setIsTriggering] = useState(false)

  const handleAnalyze = async () => {
    setIsTriggering(true)
    await triggerAnalysis()
    setIsTriggering(false)
  }

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        <RefreshCw className="w-8 h-8 text-[#A9A4A0] animate-spin mb-4" />
        <p className="text-[#A9A4A0] text-sm">Loading analysis context...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <AlertCircle className="w-10 h-10 text-[#8F0028] mb-4" />
        <p className="text-[#F5F3F1] font-medium mb-2">Failed to load website analysis</p>
        <p className="text-[#A9A4A0] text-xs mb-6 max-w-sm">{error}</p>
        <button onClick={handleAnalyze} className="px-4 py-2 bg-[#8F0028] hover:bg-[#A8002F] text-white text-[13px] font-bold rounded-lg transition-colors">
          Retry Analysis
        </button>
      </div>
    )
  }

  if (!analysis || analysis.status === 'NOT_ANALYZED') {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <Globe className="w-12 h-12 text-[#A9A4A0] mb-4" />
        <p className="text-[#F5F3F1] font-medium text-lg mb-2">Website Not Analyzed</p>
        <p className="text-[#A9A4A0] text-[13px] mb-6 max-w-sm">
          Your website hasn't been analyzed yet. Run an analysis to populate SEO signals and provide context to your AI CMO.
        </p>
        <button 
          onClick={handleAnalyze} 
          disabled={isTriggering}
          className="px-6 py-2.5 bg-[#8F0028] hover:bg-[#A8002F] text-white text-[14px] font-bold rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {isTriggering && <RefreshCw className="w-4 h-4 animate-spin" />}
          Analyze Website
        </button>
      </div>
    )
  }

  if (analysis.status === 'QUEUED' || analysis.status === 'RUNNING') {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 rounded-full bg-[#8F0028]/10 flex items-center justify-center mb-6">
          <RefreshCw className="w-8 h-8 text-[#8F0028] animate-spin" />
        </div>
        <p className="text-[#F5F3F1] font-medium text-lg mb-2">
          {analysis.status === 'QUEUED' ? 'Analysis queued...' : 'Analyzing your website...'}
        </p>
        <p className="text-[#A9A4A0] text-[13px] max-w-sm">
          This usually takes just a few seconds. We're extracting metadata, structure, and semantic context.
        </p>
      </div>
    )
  }

  if (analysis.status === 'FAILED') {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <AlertCircle className="w-12 h-12 text-[#8F0028] mb-4" />
        <p className="text-[#F5F3F1] font-medium text-lg mb-2">Analysis Failed</p>
        <p className="text-[#A9A4A0] text-[13px] mb-6 max-w-sm">
          {analysis.errors?.message || "An unexpected error occurred during analysis."}
        </p>
        <button 
          onClick={handleAnalyze} 
          disabled={isTriggering}
          className="px-6 py-2.5 bg-[#8F0028] hover:bg-[#A8002F] text-white text-[14px] font-bold rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {isTriggering ? <RefreshCw className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          Retry Analysis
        </button>
      </div>
    )
  }

  const { result_metadata } = analysis

  return (
    <div className="flex flex-col h-full bg-[#1C1A1A]">
      {/* Header */}
      <div className="px-6 py-4 flex items-center justify-between border-b border-[#373333] shrink-0 bg-[#1C1A1A] sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-[#F5F3F1] font-bold text-[15px]">
            <Globe className="w-4 h-4 text-[#8F0028]" />
            Website Analysis
          </div>
          <div className="h-1.5 w-1.5 rounded-full bg-[#00A650]"></div>
        </div>
        
        <button 
          onClick={handleAnalyze} 
          disabled={isTriggering}
          className="flex items-center gap-2 px-3 py-1.5 bg-[#242222] border border-[#373333] rounded-md text-[11px] font-bold text-[#A9A4A0] hover:text-[#F5F3F1] hover:border-[#4A4545] transition-colors disabled:opacity-50"
        >
          {isTriggering ? <RefreshCw className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
          Re-analyze
        </button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
        {/* Extracted Data Box */}
        <div className="bg-[#242222] border border-[#373333] rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-[#373333] bg-[#2A2828]/50 flex justify-between items-center">
             <h3 className="text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider">Extracted Signals</h3>
             <span className="text-[10px] text-[#A9A4A0]">EXTRACTED</span>
          </div>
          <div className="p-5 grid grid-cols-2 gap-x-8 gap-y-4">
            
            <div>
              <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Final URL</span>
              <div className="text-[13px] text-[#F5F3F1] flex items-center gap-2 truncate">
                 {result_metadata?.final_url || analysis.url}
                 {result_metadata?.https && <Lock className="w-3 h-3 text-[#00A650]" />}
              </div>
            </div>

            <div>
              <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">HTTP Status</span>
              <div className="text-[13px] text-[#F5F3F1] flex items-center gap-2">
                 {result_metadata?.http_status || 'Unknown'}
                 {result_metadata?.http_status === 200 && <CheckCircle2 className="w-3.5 h-3.5 text-[#00A650]" />}
              </div>
            </div>

            <div className="col-span-2">
              <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Title ({result_metadata?.title_length || 0} chars)</span>
              <p className="text-[13px] text-[#F5F3F1] font-medium">{result_metadata?.title || 'No Title Found'}</p>
            </div>

            <div className="col-span-2">
              <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Meta Description</span>
              <p className="text-[13px] text-[#A9A4A0]">{result_metadata?.meta_description || 'No Meta Description'}</p>
            </div>

            <div>
              <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Structure</span>
              <ul className="text-[12px] text-[#A9A4A0] space-y-1">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className={`w-3 h-3 ${result_metadata?.h1_exists ? 'text-[#00A650]' : 'text-[#8F0028]'}`} />
                  {result_metadata?.h1_count} H1 Tag(s)
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className={`w-3 h-3 ${result_metadata?.h2_count ? 'text-[#00A650]' : 'text-[#A9A4A0]'}`} />
                  {result_metadata?.h2_count} H2 Tag(s)
                </li>
              </ul>
            </div>

            <div>
              <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Technical SEO</span>
              <ul className="text-[12px] text-[#A9A4A0] space-y-1">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className={`w-3 h-3 ${result_metadata?.canonical_exists ? 'text-[#00A650]' : 'text-[#8F0028]'}`} />
                  Canonical Tag
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className={`w-3 h-3 ${result_metadata?.robots_exists ? 'text-[#00A650]' : 'text-[#8F0028]'}`} />
                  robots.txt
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className={`w-3 h-3 ${result_metadata?.sitemap_exists ? 'text-[#00A650]' : 'text-[#8F0028]'}`} />
                  sitemap.xml
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className={`w-3 h-3 ${result_metadata?.open_graph_exists ? 'text-[#00A650]' : 'text-[#A9A4A0]'}`} />
                  Open Graph Data
                </li>
              </ul>
            </div>

            <div>
              <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Content</span>
              <div className="text-[13px] text-[#F5F3F1]">
                 {result_metadata?.word_count || 0} Words
              </div>
            </div>

            <div>
              <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Images</span>
              <div className="text-[13px] text-[#F5F3F1]">
                 {result_metadata?.image_count || 0} Total
                 {result_metadata?.images_missing_alt ? (
                   <span className="ml-2 text-[#8F0028]">({result_metadata.images_missing_alt} missing alt text)</span>
                 ) : null}
              </div>
            </div>

            <div>
              <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Internal Links</span>
              <div className="text-[13px] text-[#F5F3F1]">{result_metadata?.internal_links || 0}</div>
            </div>

            <div>
              <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">External Links</span>
              <div className="text-[13px] text-[#F5F3F1]">{result_metadata?.external_links || 0}</div>
            </div>

          </div>
        </div>

        {/* Inferred Context */}
        <div className="bg-[#242222] border border-[#373333] rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-[#373333] bg-[#2A2828]/50 flex justify-between items-center">
             <h3 className="text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider">Business Context</h3>
             <span className="text-[10px] text-[#A9A4A0]">INFERRED</span>
          </div>
          <div className="p-5 space-y-4">
             <div>
               <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Topics</span>
               <div className="flex flex-wrap gap-2">
                 {analysis.analysis_results?.inferred_topics?.map((topic: string) => (
                   <span key={topic} className="px-2 py-1 bg-[#2E2B2B] rounded text-[11px] text-[#F5F3F1] border border-[#373333]">{topic}</span>
                 )) || <span className="text-[12px] text-[#A9A4A0]">No topics inferred.</span>}
               </div>
             </div>
             <div>
               <span className="block text-[11px] font-bold text-[#A9A4A0] mb-1">Value Proposition</span>
               <p className="text-[13px] text-[#A9A4A0] italic">
                 "{analysis.analysis_results?.value_proposition || 'Not enough data to infer.'}"
               </p>
             </div>
          </div>
        </div>

      </div>
    </div>
  )
}
