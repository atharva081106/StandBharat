"use client"
import React, { createContext, useContext, useState, useEffect } from 'react'
import { useAppProvider } from './index'

// ── Hook: useAuth ────────────────────────────────────────────────
export { AppProvider as AuthProvider } from './index'

export const useAuth = () => {
  const { auth } = useAppProvider()
  return auth
}

export const useDashboard = () => {
  const { dashboard } = useAppProvider()
  return dashboard
}

export const useOpportunity = () => {
  const { opportunity } = useAppProvider()
  return opportunity
}

export const useOrchestrator = () => {
  const { orchestrator } = useAppProvider()
  return orchestrator
}

export const useAiCmo = () => {
  const { aiCmo } = useAppProvider()
  return aiCmo
}

export const useAgents = () => {
  const { agents } = useAppProvider()
  return agents
}

// ── BrandBrain: Context with caching ─────────────────────────────
interface BrandBrainState {
  brandBrain: any | null
  loading: boolean
  error: string | null
  refresh: () => void
}

const BrandBrainContext = createContext<BrandBrainState | undefined>(undefined)

export function BrandBrainContextProvider({ children }: { children: React.ReactNode }) {
  const { brandBrain: provider, auth } = useAppProvider()
  const [brandBrain, setBrandBrain] = useState<any | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetch = async () => {
    if (!auth.activeBrand) return
    setLoading(true)
    setError(null)
    try {
      const data = await provider.getContext()
      setBrandBrain(data)
    } catch (e: any) {
      setError(e.message || 'Failed to load brand context')
      setBrandBrain(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (auth.authState === 'loggedIn' && auth.activeBrand) {
      fetch()
    }
  }, [auth.authState, auth.activeBrand?.id])

  return (
    <BrandBrainContext.Provider value={{ brandBrain, loading, error, refresh: fetch }}>
      {children}
    </BrandBrainContext.Provider>
  )
}

export const useBrandBrain = (): BrandBrainState => {
  const ctx = useContext(BrandBrainContext)
  if (!ctx) throw new Error('useBrandBrain must be used within BrandBrainContextProvider')
  return ctx
}
