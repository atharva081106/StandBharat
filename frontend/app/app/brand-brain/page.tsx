"use client"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAppProvider } from '@/lib/providers'
import { useEffect, useState } from 'react'

export default function BrandBrain() {
  const { brandBrain } = useAppProvider()
  const [context, setContext] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchContext = async () => {
      try {
        const data = await brandBrain.getContext()
        setContext(data)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchContext()
  }, [brandBrain])

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center text-[var(--color-text-muted)]">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 rounded-full border-4 border-[var(--color-bg-subtle)] border-t-[var(--color-brand-accent)] animate-spin"></div>
          <p className="text-sm font-medium">Loading Brand Brain...</p>
        </div>
      </div>
    )
  }

  const b = context?.brand || {}
  const voice = context?.voice || {}
  const positioning = context?.positioning || {}
  const strategy = context?.strategy || {}
  const audiences = context?.audiences || []
  const products = context?.products || []
  const goals = context?.goals || []
  const competitors = context?.competitors || []
  const documents = context?.documents || []

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col gap-2 border-b border-[var(--color-border-primary)] pb-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-text-primary)]">Brand Brain</h1>
        </div>
        <p className="text-[var(--color-text-tertiary)] text-lg">The central intelligence layer your AI agents use to understand your business.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        
        {/* Brand Overview */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="text-base">Business Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm flex-1 flex flex-col">
            <div className="space-y-3 flex-1">
              {Object.entries({
                Name: b.name,
                Industry: b.industry,
                Category: b.category,
                Location: b.location,
                Mission: b.mission,
                Vision: b.vision,
                Values: b.values,
                Tagline: b.tagline
              }).map(([key, value]) => (
                <div key={key}>
                  <span className="font-semibold text-[var(--color-text-primary)]">{key}: </span> 
                  <span className={value ? "text-[var(--color-text-secondary)]" : "text-[var(--color-text-muted)] italic"}>
                    {value || "Not defined"}
                  </span>
                </div>
              ))}
            </div>
            <button className="text-sm font-medium text-[var(--color-brand-accent)] hover:text-[var(--color-brand-accent-hover)] text-left mt-4 transition-colors">Edit Overview</button>
          </CardContent>
        </Card>
        
        {/* Brand Voice */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="text-base">Brand Voice</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm flex-1 flex flex-col">
            <div className="flex-1 space-y-4">
              <div className="flex gap-2 flex-wrap">
                {voice.tone ? <Badge variant="secondary">{voice.tone}</Badge> : <Badge variant="outline">No tone specified</Badge>}
                {voice.personality && <Badge variant="secondary">{voice.personality}</Badge>}
              </div>
              <div className="space-y-2">
                <div>
                  <span className="font-semibold text-[var(--color-text-primary)]">Style: </span> 
                  <span className={voice.writing_style ? "text-[var(--color-text-secondary)]" : "text-[var(--color-text-muted)] italic"}>
                    {voice.writing_style || "Not defined"}
                  </span>
                </div>
                <div>
                  <span className="font-semibold text-[var(--color-text-primary)]">Formality: </span> 
                  <span className={voice.formality ? "text-[var(--color-text-secondary)]" : "text-[var(--color-text-muted)] italic"}>
                    {voice.formality || "Not defined"}
                  </span>
                </div>
              </div>
            </div>
            <button className="text-sm font-medium text-[var(--color-brand-accent)] hover:text-[var(--color-brand-accent-hover)] text-left transition-colors">Edit Voice</button>
          </CardContent>
        </Card>

        {/* Positioning */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="text-base">Positioning</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm flex-1 flex flex-col">
            <div className="flex-1 space-y-3">
              <div>
                <span className="font-semibold text-[var(--color-text-primary)] block mb-1">Statement</span> 
                <span className={positioning.positioning_statement ? "text-[var(--color-text-secondary)] leading-relaxed" : "text-[var(--color-text-muted)] italic"}>
                  {positioning.positioning_statement || "Not defined"}
                </span>
              </div>
              <div>
                <span className="font-semibold text-[var(--color-text-primary)] block mb-1">Unique Value Proposition</span> 
                <span className={positioning.unique_value_proposition ? "text-[var(--color-text-secondary)] leading-relaxed" : "text-[var(--color-text-muted)] italic"}>
                  {positioning.unique_value_proposition || "Not defined"}
                </span>
              </div>
            </div>
            <button className="text-sm font-medium text-[var(--color-brand-accent)] hover:text-[var(--color-brand-accent-hover)] text-left mt-4 transition-colors">Edit Positioning</button>
          </CardContent>
        </Card>

        {/* Audiences */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Audiences</span>
              <Badge variant="secondary">{audiences.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm flex-1 flex flex-col">
            <div className="flex-1 space-y-3">
              {audiences.length > 0 ? audiences.map((aud: any) => (
                <div key={aud.id} className="p-3 border border-[var(--color-border-primary)] rounded-lg bg-[var(--color-bg-primary)]">
                  <div className="font-semibold text-[var(--color-text-primary)]">{aud.name}</div>
                  <div className="text-[var(--color-text-tertiary)] mt-1.5 text-xs leading-relaxed">{aud.description}</div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center h-full py-6 text-center text-[var(--color-text-muted)] border border-dashed border-[var(--color-border-primary)] rounded-lg">
                  <span className="italic">No audiences defined</span>
                </div>
              )}
            </div>
            <button className="text-sm font-medium text-[var(--color-brand-accent)] hover:text-[var(--color-brand-accent-hover)] text-left mt-2 transition-colors">+ Add Audience</button>
          </CardContent>
        </Card>

        {/* Products */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Products / Services</span>
              <Badge variant="secondary">{products.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm flex-1 flex flex-col">
            <div className="flex-1 space-y-3">
              {products.length > 0 ? products.map((prod: any) => (
                <div key={prod.id} className="p-3 border border-[var(--color-border-primary)] rounded-lg bg-[var(--color-bg-primary)]">
                  <div className="flex items-start justify-between gap-2">
                    <div className="font-semibold text-[var(--color-text-primary)]">{prod.name}</div>
                    {prod.price && <span className="text-xs font-medium text-[var(--color-brand-accent)] bg-[var(--color-brand-accent-subtle)] px-2 py-0.5 rounded whitespace-nowrap">{prod.price}</span>}
                  </div>
                  <div className="text-[var(--color-text-tertiary)] mt-1.5 text-xs leading-relaxed">{prod.description}</div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center h-full py-6 text-center text-[var(--color-text-muted)] border border-dashed border-[var(--color-border-primary)] rounded-lg">
                  <span className="italic">No products defined</span>
                </div>
              )}
            </div>
            <button className="text-sm font-medium text-[var(--color-brand-accent)] hover:text-[var(--color-brand-accent-hover)] text-left mt-2 transition-colors">+ Add Product</button>
          </CardContent>
        </Card>

        {/* Competitors */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Competitors</span>
              <Badge variant="secondary">{competitors.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm flex-1 flex flex-col">
            <div className="flex-1 space-y-3">
              {competitors.length > 0 ? competitors.map((comp: any) => (
                <div key={comp.id} className="p-3 border border-[var(--color-border-primary)] rounded-lg bg-[var(--color-bg-primary)]">
                  <div className="font-semibold text-[var(--color-text-primary)]">{comp.name}</div>
                  <div className="text-[var(--color-text-tertiary)] mt-1.5 text-xs leading-relaxed line-clamp-2">
                    <span className="font-medium">Weakness: </span>{comp.weaknesses}
                  </div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center h-full py-6 text-center text-[var(--color-text-muted)] border border-dashed border-[var(--color-border-primary)] rounded-lg px-4">
                  <p className="font-medium text-[var(--color-text-primary)] mb-1">No competitors added yet.</p>
                  <span className="text-xs">Adding competitors helps the AI CMO identify positioning gaps and growth opportunities.</span>
                </div>
              )}
            </div>
            <button className="text-sm font-medium text-[var(--color-brand-accent)] hover:text-[var(--color-brand-accent-hover)] text-left mt-2 transition-colors">+ Add Competitor</button>
          </CardContent>
        </Card>

        {/* Goals */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Goals</span>
              <Badge variant="secondary">{goals.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm flex-1 flex flex-col">
            <div className="flex-1 space-y-3">
              {goals.length > 0 ? goals.map((goal: any) => (
                <div key={goal.id} className="p-3 border border-[var(--color-border-primary)] rounded-lg bg-[var(--color-bg-primary)] flex justify-between items-center gap-4">
                  <div className="min-w-0">
                    <div className="font-semibold text-[var(--color-text-primary)] truncate">{goal.goal}</div>
                    <div className="text-[var(--color-text-tertiary)] text-xs mt-1">Target: {goal.target_value}</div>
                  </div>
                  <Badge variant="outline" className="shrink-0">{goal.current_value || 'No data'}</Badge>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center h-full py-6 text-center text-[var(--color-text-muted)] border border-dashed border-[var(--color-border-primary)] rounded-lg">
                  <span className="italic">No goals defined</span>
                </div>
              )}
            </div>
            <button className="text-sm font-medium text-[var(--color-brand-accent)] hover:text-[var(--color-brand-accent-hover)] text-left mt-2 transition-colors">+ Add Goal</button>
          </CardContent>
        </Card>

        {/* Strategy */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="text-base">Strategy</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm flex-1 flex flex-col">
            <div className="flex-1 space-y-3">
              <div>
                <span className="font-semibold text-[var(--color-text-primary)] block mb-1">Business Strategy</span> 
                <span className={strategy.business_strategy ? "text-[var(--color-text-secondary)] leading-relaxed" : "text-[var(--color-text-muted)] italic"}>
                  {strategy.business_strategy || "Not defined"}
                </span>
              </div>
              <div>
                <span className="font-semibold text-[var(--color-text-primary)] block mb-1">Marketing Strategy</span> 
                <span className={strategy.marketing_strategy ? "text-[var(--color-text-secondary)] leading-relaxed" : "text-[var(--color-text-muted)] italic"}>
                  {strategy.marketing_strategy || "Not defined"}
                </span>
              </div>
            </div>
            <button className="text-sm font-medium text-[var(--color-brand-accent)] hover:text-[var(--color-brand-accent-hover)] text-left mt-4 transition-colors">Edit Strategy</button>
          </CardContent>
        </Card>

        {/* Documents */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Documents</span>
              <Badge variant="secondary">{documents.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 flex-1 flex flex-col">
            <div className="flex-1 space-y-2">
               {documents.length > 0 ? documents.map((doc: any) => (
                 <div key={doc.id} className="p-3 border border-[var(--color-border-primary)] rounded-lg bg-[var(--color-bg-primary)] text-sm flex justify-between items-center gap-4 hover:bg-[var(--color-bg-subtle)] transition-colors cursor-pointer">
                   <span className="truncate font-medium text-[var(--color-text-secondary)]">{doc.name}</span>
                   <Badge variant="success" className="shrink-0 text-[10px] uppercase tracking-wider px-1.5 py-0">Parsed</Badge>
                 </div>
               )) : (
                <div className="flex flex-col items-center justify-center h-full py-6 text-center text-[var(--color-text-muted)] border border-dashed border-[var(--color-border-primary)] rounded-lg">
                  <span className="italic">No documents uploaded</span>
                </div>
               )}
            </div>
            <button className="text-sm font-medium text-[var(--color-brand-accent)] hover:text-[var(--color-brand-accent-hover)] text-left mt-3 transition-colors">+ Upload Document</button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
