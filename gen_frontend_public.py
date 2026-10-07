import os
from pathlib import Path

BASE_DIR = Path("frontend")

def write_file(path, content):
    full_path = BASE_DIR / path
    os.makedirs(full_path.parent, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# --- app/layout.tsx ---
layout_tsx = """
import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { AuthProvider } from '@/lib/providers/MockProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'StandBharat - AI CMO',
  description: 'Your AI CMO for Real Growth',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#FAFAF8] text-gray-900`}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
"""
write_file("app/layout.tsx", layout_tsx)

# --- app/page.tsx ---
page_tsx = """
import { redirect } from 'next/navigation'

export default function RootPage() {
  redirect('/landingpage')
}
"""
write_file("app/page.tsx", page_tsx)

# --- app/landingpage/page.tsx ---
landing_tsx = """
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#FAFAF8]">
      <header className="flex justify-between items-center px-8 py-6 border-b border-[#E5E5E5] bg-white">
        <div className="font-bold text-xl tracking-tighter text-[#111111]">StandBharat</div>
        <nav className="hidden md:flex space-x-8 text-sm font-medium text-[#525252]">
          <Link href="#product" className="hover:text-[#111111]">Product</Link>
          <Link href="#solutions" className="hover:text-[#111111]">Solutions</Link>
          <Link href="/pricing" className="hover:text-[#111111]">Pricing</Link>
          <Link href="#resources" className="hover:text-[#111111]">Resources</Link>
          <Link href="#company" className="hover:text-[#111111]">Company</Link>
        </nav>
        <div className="flex space-x-4">
          <Link href="/login">
            <Button variant="ghost">Sign In</Button>
          </Link>
          <Link href="/signup">
            <Button>Get Started</Button>
          </Link>
        </div>
      </header>
      
      <main className="flex-1 flex flex-col items-center pt-32 pb-24 px-6 text-center">
        <div className="mb-6 inline-flex items-center rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-sm font-medium text-orange-600">
          AI MARKETING OPERATING SYSTEM
        </div>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-[#111111] max-w-4xl">
          Your AI CMO <br/>
          <span className="text-orange-500">for Real Growth</span>
        </h1>
        <p className="mt-8 text-xl text-[#525252] max-w-2xl leading-relaxed">
          Research, strategize, create, execute and measure — with autonomous AI agents that turn marketing activity into revenue.
        </p>
        <div className="mt-12 flex space-x-4">
          <Link href="/signup">
            <Button size="lg" className="text-base h-14 px-8">Get Started Free</Button>
          </Link>
          <Button size="lg" variant="outline" className="text-base h-14 px-8">Watch Demo</Button>
        </div>
        
        {/* Placeholder for Product Preview */}
        <div className="mt-24 w-full max-w-6xl aspect-video bg-white border border-[#E5E5E5] rounded-xl shadow-sm flex items-center justify-center">
          <span className="text-[#737373] text-lg font-medium">Interactive Product Preview</span>
        </div>
        
        {/* Trusted Teams */}
        <div className="mt-24 w-full max-w-4xl border-t border-[#E5E5E5] pt-12">
          <p className="text-sm font-medium text-[#737373] uppercase tracking-widest mb-8">Trusted by leading marketing teams</p>
          <div className="flex justify-center gap-12 text-[#525252] opacity-50 grayscale">
             {/* Mock logos */}
             <div className="text-2xl font-bold">AcmeCorp</div>
             <div className="text-2xl font-bold">Globex</div>
             <div className="text-2xl font-bold">Soylent</div>
          </div>
        </div>
      </main>
    </div>
  )
}
"""
write_file("app/landingpage/page.tsx", landing_tsx)

# --- app/login/page.tsx ---
login_tsx = """
"use client"
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/lib/providers/MockProvider'

export default function Login() {
  const router = useRouter()
  const { setAuthState } = useAuth()

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    setAuthState('loggedIn')
    router.push('/app/command-center')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#FAFAF8] px-4">
      <div className="max-w-md w-full p-8 bg-white rounded-xl shadow-sm border border-[#E5E5E5]">
        <div className="text-center mb-8">
          <div className="font-bold text-xl text-orange-500 mb-6">StandBharat</div>
          <h2 className="text-2xl font-semibold text-[#111111]">Welcome back</h2>
        </div>
        
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[#111111] mb-1">Email</label>
            <Input type="email" placeholder="name@company.com" required />
          </div>
          <div>
            <div className="flex justify-between mb-1">
               <label className="block text-sm font-medium text-[#111111]">Password</label>
               <Link href="#" className="text-sm text-orange-500 hover:underline">Forgot password?</Link>
            </div>
            <Input type="password" required />
          </div>
          
          <div className="flex items-center">
            <input type="checkbox" id="remember" className="h-4 w-4 rounded border-gray-300 text-orange-500 focus:ring-orange-500" />
            <label htmlFor="remember" className="ml-2 block text-sm text-[#525252]">Remember me</label>
          </div>
          
          <Button type="submit" className="w-full">Sign In</Button>
          
          <div className="mt-4 text-center text-sm text-[#737373]">
            <span className="px-2 bg-white">Or</span>
          </div>
          
          <Button type="button" variant="outline" className="w-full mt-4" onClick={() => handleLogin({preventDefault: () => {}} as any)}>
            Continue with Google
          </Button>
        </form>
        
        <p className="mt-8 text-center text-sm text-[#525252]">
          Don't have an account? <Link href="/signup" className="text-orange-500 hover:underline font-medium">Create account</Link>
        </p>
      </div>
    </div>
  )
}
"""
write_file("app/login/page.tsx", login_tsx)

# --- app/signup/page.tsx ---
signup_tsx = """
"use client"
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/lib/providers/MockProvider'

export default function Signup() {
  const router = useRouter()
  const { setAuthState } = useAuth()

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault()
    setAuthState('onboarding')
    router.push('/onboarding')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#FAFAF8] px-4">
      <div className="max-w-md w-full p-8 bg-white rounded-xl shadow-sm border border-[#E5E5E5]">
        <div className="text-center mb-8">
          <div className="font-bold text-xl text-orange-500 mb-6">StandBharat</div>
          <h2 className="text-2xl font-semibold text-[#111111]">Create account</h2>
        </div>
        
        <form onSubmit={handleSignup} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[#111111] mb-1">Email</label>
            <Input type="email" placeholder="name@company.com" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#111111] mb-1">Password</label>
            <Input type="password" required />
          </div>
          
          <Button type="submit" className="w-full">Get Started</Button>
          
          <div className="mt-4 text-center text-sm text-[#737373]">
            <span className="px-2 bg-white">Or</span>
          </div>
          
          <Button type="button" variant="outline" className="w-full mt-4" onClick={() => handleSignup({preventDefault: () => {}} as any)}>
            Continue with Google
          </Button>
        </form>
        
        <p className="mt-8 text-center text-sm text-[#525252]">
          Already have an account? <Link href="/login" className="text-orange-500 hover:underline font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
"""
write_file("app/signup/page.tsx", signup_tsx)

# --- app/onboarding/page.tsx ---
onboarding_tsx = """
"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/lib/providers/MockProvider'

const steps = ["Business", "Brand", "Audience", "Goals", "Competitors", "AI Setup", "Ready"]

export default function Onboarding() {
  const [stepIdx, setStepIdx] = useState(0)
  const router = useRouter()
  const { setAuthState } = useAuth()

  const handleNext = () => {
    if (stepIdx < steps.length - 1) {
      setStepIdx(stepIdx + 1)
    } else {
      setAuthState('onboardingComplete')
      router.push('/app/command-center')
    }
  }

  const handleBack = () => {
    if (stepIdx > 0) setStepIdx(stepIdx - 1)
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#FAFAF8]">
      <header className="px-8 py-4 border-b border-[#E5E5E5] bg-white flex justify-between items-center">
        <div className="font-bold text-orange-500">StandBharat</div>
        <div className="text-sm font-medium text-[#737373]">
          Step {stepIdx + 1} of {steps.length}: {steps[stepIdx]}
        </div>
      </header>
      
      <main className="flex-1 flex items-center justify-center p-6">
        <div className="max-w-2xl w-full bg-white rounded-xl shadow-sm border border-[#E5E5E5] p-10">
          
          {stepIdx === 0 && (
            <div className="animate-in fade-in duration-500">
              <h2 className="text-2xl font-bold text-[#111111] mb-6">Tell us about your business</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Business name</label>
                  <Input placeholder="Acme Corp" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Website</label>
                  <Input placeholder="https://acme.com" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Business description</label>
                  <textarea className="w-full rounded-md border border-[#E5E5E5] p-3 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500" rows={4}></textarea>
                </div>
              </div>
            </div>
          )}

          {stepIdx === 1 && (
            <div className="animate-in fade-in duration-500">
              <h2 className="text-2xl font-bold text-[#111111] mb-6">Build your Brand Brain</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Value proposition</label>
                  <Input placeholder="What makes you unique?" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Brand voice</label>
                  <div className="flex flex-wrap gap-2">
                    {["Professional", "Friendly", "Bold", "Technical", "Premium", "Playful"].map(v => (
                      <span key={v} className="px-4 py-2 border border-[#E5E5E5] rounded-full text-sm cursor-pointer hover:border-orange-500">{v}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {(stepIdx > 1 && stepIdx < 5) && (
            <div className="animate-in fade-in duration-500">
              <h2 className="text-2xl font-bold text-[#111111] mb-6">{steps[stepIdx]}</h2>
              <p className="text-[#525252] mb-6">Configuring your {steps[stepIdx].toLowerCase()} parameters...</p>
              <Input placeholder={`Enter ${steps[stepIdx].toLowerCase()} info...`} />
            </div>
          )}
          
          {stepIdx === 5 && (
            <div className="animate-in fade-in duration-500">
              <h2 className="text-2xl font-bold text-[#111111] mb-6">Assembling AI Team</h2>
              <div className="grid grid-cols-2 gap-4">
                {["Analytics Agent", "SEO Agent", "GEO Agent", "Writer Agent", "Growth Agent"].map(agent => (
                  <div key={agent} className="p-4 border border-[#E5E5E5] rounded-md flex items-center justify-between">
                    <span className="font-medium">{agent}</span>
                    <span className="text-green-500 text-sm">Ready</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {stepIdx === 6 && (
            <div className="animate-in fade-in duration-500 text-center py-8">
              <h2 className="text-3xl font-bold text-[#111111] mb-4">Your AI marketing system is ready</h2>
              <p className="text-[#525252] mb-8">Brand, Audience, Goals, Competitors, and AI team have been configured.</p>
            </div>
          )}

          <div className="mt-10 flex justify-between border-t border-[#E5E5E5] pt-6">
            <Button variant="outline" onClick={handleBack} disabled={stepIdx === 0}>Back</Button>
            <Button onClick={handleNext}>
              {stepIdx === steps.length - 1 ? 'Enter Command Center →' : 'Continue'}
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
"""
write_file("app/onboarding/page.tsx", onboarding_tsx)

print("Public pages generated.")
