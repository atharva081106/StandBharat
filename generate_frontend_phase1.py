import os
from pathlib import Path

BASE_DIR = Path("frontend")

def write_file(path, content):
    full_path = BASE_DIR / path
    os.makedirs(full_path.parent, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# lib/api.ts
api_ts = """
const API_URL = "http://localhost:8000/api";

export async function fetchApi(endpoint: string, options: RequestInit = {}) {
    options.credentials = "include"; // For cookies
    if (!options.headers) {
        options.headers = {};
    }
    (options.headers as any)["Content-Type"] = "application/json";
    
    const response = await fetch(`${API_URL}${endpoint}`, options);
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "API Error");
    }
    return response.json();
}
"""
write_file("lib/api.ts", api_ts)

# app/layout.tsx
layout_tsx = """
import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

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
      <body className={`${inter.className} bg-white text-gray-900`}>{children}</body>
    </html>
  )
}
"""
write_file("app/layout.tsx", layout_tsx)

# app/page.tsx (Landing Page)
page_tsx = """
import Link from 'next/link'

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-between items-center p-6 border-b">
        <div className="font-bold text-xl tracking-tighter text-orange-500">StandBharat</div>
        <div className="space-x-4">
          <Link href="/login" className="text-gray-600 hover:text-black">Sign In</Link>
          <Link href="/signup" className="bg-orange-500 text-white px-4 py-2 rounded-md font-medium hover:bg-orange-600">Get Started Free</Link>
        </div>
      </header>
      
      <main className="flex-1 flex flex-col items-center justify-center text-center p-6 mt-20">
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-gray-900 max-w-4xl">
          Your AI CMO for <span className="text-orange-500">Real Growth</span>
        </h1>
        <p className="mt-6 text-xl text-gray-500 max-w-2xl">
          Research, strategize, create, execute and measure — with autonomous AI agents that turn marketing activity into revenue.
        </p>
        <div className="mt-10 space-x-4">
          <Link href="/signup" className="bg-orange-500 text-white px-8 py-4 rounded-md font-medium text-lg hover:bg-orange-600">Start Your Engine</Link>
          <button className="border border-gray-300 text-gray-700 px-8 py-4 rounded-md font-medium text-lg hover:bg-gray-50">Watch Demo</button>
        </div>
      </main>
    </div>
  )
}
"""
write_file("app/page.tsx", page_tsx)

# app/login/page.tsx
login_tsx = """
"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { fetchApi } from '@/lib/api'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await fetchApi('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      })
      router.push('/app/command-center')
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-sm border border-gray-100">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Sign in to StandBharat</h2>
        </div>
        {error && <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-md">{error}</div>}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input type="email" value={email} onChange={e=>setEmail(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input type="password" value={password} onChange={e=>setPassword(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md" required />
          </div>
          <button type="submit" className="w-full bg-orange-500 text-white p-2 rounded-md hover:bg-orange-600 font-medium">Sign In</button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          Don't have an account? <Link href="/signup" className="text-orange-500 hover:underline">Sign up</Link>
        </p>
      </div>
    </div>
  )
}
"""
write_file("app/login/page.tsx", login_tsx)

# app/signup/page.tsx
signup_tsx = """
"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { fetchApi } from '@/lib/api'

export default function Signup() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await fetchApi('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      })
      // auto login after signup
      await fetchApi('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      })
      router.push('/onboarding')
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-sm border border-gray-100">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Create your account</h2>
        </div>
        {error && <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-md">{error}</div>}
        <form onSubmit={handleSignup} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input type="email" value={email} onChange={e=>setEmail(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input type="password" value={password} onChange={e=>setPassword(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md" required />
          </div>
          <button type="submit" className="w-full bg-orange-500 text-white p-2 rounded-md hover:bg-orange-600 font-medium">Create Account</button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          Already have an account? <Link href="/login" className="text-orange-500 hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
"""
write_file("app/signup/page.tsx", signup_tsx)

# app/onboarding/page.tsx
onboarding_tsx = """
"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { fetchApi } from '@/lib/api'

export default function Onboarding() {
  const [step, setStep] = useState(1)
  const [workspaceName, setWorkspaceName] = useState('')
  const [brandName, setBrandName] = useState('')
  const [workspaceId, setWorkspaceId] = useState('')
  const router = useRouter()

  const handleCreateWorkspace = async () => {
    const res = await fetchApi('/workspaces/', {
      method: 'POST',
      body: JSON.stringify({ name: workspaceName })
    })
    setWorkspaceId(res.id)
    setStep(2)
  }

  const handleCreateBrand = async () => {
    await fetchApi('/brands/', {
      method: 'POST',
      body: JSON.stringify({ name: brandName, workspace_id: workspaceId })
    })
    router.push('/app/command-center')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-sm border border-gray-100">
        <h2 className="text-2xl font-bold mb-6">Let's set up your account</h2>
        
        {step === 1 && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Workspace Name</label>
              <input type="text" value={workspaceName} onChange={e=>setWorkspaceName(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md" placeholder="e.g. Acme Corp" />
            </div>
            <button onClick={handleCreateWorkspace} className="w-full bg-orange-500 text-white p-2 rounded-md">Continue</button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Brand Name</label>
              <input type="text" value={brandName} onChange={e=>setBrandName(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md" placeholder="e.g. Acme SaaS" />
            </div>
            <button onClick={handleCreateBrand} className="w-full bg-orange-500 text-white p-2 rounded-md">Go to Dashboard</button>
          </div>
        )}
      </div>
    </div>
  )
}
"""
write_file("app/onboarding/page.tsx", onboarding_tsx)

# app/app/layout.tsx (Application Shell)
app_layout_tsx = """
import Link from 'next/link'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b">
          <div className="font-bold text-lg text-orange-500">StandBharat</div>
        </div>
        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          <Link href="/app/command-center" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-900 bg-gray-100">Command Center</Link>
          <Link href="/app/ai-cmo" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50">AI CMO</Link>
          <Link href="/app/brand-brain" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50">Brand Brain</Link>
          <div className="my-4 border-t border-gray-200"></div>
          <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase">Agents</div>
          <Link href="/app/agents" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50">Directory</Link>
          <div className="my-4 border-t border-gray-200"></div>
          <Link href="/app/integrations" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50">Integrations</Link>
          <Link href="/app/settings" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50">Settings</Link>
        </nav>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-6 justify-between">
          <div className="text-sm font-medium text-gray-500">Workspace / Brand</div>
          <div className="flex items-center space-x-4">
             <div className="text-sm font-medium text-gray-700">Profile</div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
"""
write_file("app/app/layout.tsx", app_layout_tsx)

# app/app/command-center/page.tsx
command_center_tsx = """
export default function CommandCenter() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Command Center</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {['Revenue', 'Leads', 'Conversion Rate', 'AI Spend'].map((m) => (
          <div key={m} className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <div className="text-sm text-gray-500 font-medium">{m}</div>
            <div className="mt-2 text-2xl font-bold text-gray-900">--</div>
          </div>
        ))}
      </div>
      
      <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-100 text-center">
        <p className="text-gray-500">No marketing data yet.<br/>Connect your analytics sources to start measuring performance.</p>
      </div>
    </div>
  )
}
"""
write_file("app/app/command-center/page.tsx", command_center_tsx)

# app/app/ai-cmo/page.tsx
ai_cmo_tsx = """
export default function AICMO() {
  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-gray-100">
      <div className="p-4 border-b">
        <h2 className="text-lg font-bold">AI CMO</h2>
      </div>
      <div className="flex-1 p-4 overflow-y-auto flex items-center justify-center">
        <div className="text-gray-500 text-center">
          AI provider not configured.
        </div>
      </div>
      <div className="p-4 border-t">
        <input type="text" placeholder="Ask your AI CMO to find opportunities..." className="w-full p-3 border border-gray-300 rounded-md" disabled />
      </div>
    </div>
  )
}
"""
write_file("app/app/ai-cmo/page.tsx", ai_cmo_tsx)

# app/app/brand-brain/page.tsx
brand_brain_tsx = """
export default function BrandBrain() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Brand Brain</h1>
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
        <h3 className="font-bold text-lg mb-4">Brand Knowledge</h3>
        <p className="text-gray-500">Upload your product docs and provide context so agents understand your business.</p>
      </div>
    </div>
  )
}
"""
write_file("app/app/brand-brain/page.tsx", brand_brain_tsx)

# Add globals.css to clear defaults
write_file("app/globals.css", "@import 'tailwindcss';")

print("Frontend React components generated.")
