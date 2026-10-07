"use client"
import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/providers/MockProvider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export function AuthModal() {
  const router = useRouter()
  const { authModalOpen, setAuthModalOpen, login, signup } = useAuth()
  const [isLogin, setIsLogin] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [loading, setLoading] = useState(false)

  React.useEffect(() => {
    const openLogin = () => { setAuthModalOpen(true); setIsLogin(true); };
    const openSignup = () => { setAuthModalOpen(true); setIsLogin(false); };
    window.addEventListener('open-auth-login', openLogin);
    window.addEventListener('open-auth-signup', openSignup);
    return () => {
      window.removeEventListener('open-auth-login', openLogin);
      window.removeEventListener('open-auth-signup', openSignup);
    }
  }, [setAuthModalOpen]);

  if (!authModalOpen) return null;

  const handleClose = () => {
    setAuthModalOpen(false)
    setIsLogin(false)
    setEmail("")
    setPassword("")
    setName("")
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (isLogin) {
        await login(email, password)
        router.push('/app/command-center')
      } else {
        await signup(email, password, name || email.split('@')[0])
        router.push('/onboarding')
      }
      setAuthModalOpen(false)
    } catch (err) {
      alert(isLogin ? "Login failed" : "Signup failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/40 backdrop-blur-[2px]">
      <div 
        className="absolute inset-0" 
        onClick={handleClose}
      />
      <div className="relative bg-white rounded-[24px] shadow-2xl flex w-full max-w-[880px] max-h-[90vh] overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Close Button */}
        <button 
          onClick={handleClose}
          className="absolute top-4 right-4 sm:top-5 sm:right-5 z-20 w-8 h-8 flex items-center justify-center rounded-full bg-black/5 hover:bg-black/10 transition-colors text-black/50 hover:text-black"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Left Side: Form */}
        <div className="flex-1 flex flex-col p-6 sm:p-10 justify-center bg-white overflow-y-auto">
          <div className="mb-6">
            <h2 className="text-2xl sm:text-[28px] font-bold text-[#111111] tracking-tight leading-tight mb-1.5">
              {isLogin ? 'Welcome back' : 'Create your account'}
            </h2>
            <p className="text-[#5A5A5A] font-medium text-sm">
              {isLogin ? 'Log in to your StandBharat workspace.' : 'Start your journey with AI-powered marketing.'}
            </p>
          </div>

          <div className="space-y-2.5 mb-5">
            <Button variant="outline" className="w-full h-10 bg-white hover:bg-[#FAF8F3] border-[#E8E4DC] text-[#111111] font-bold text-sm rounded-xl gap-2.5">
              <svg viewBox="0 0 24 24" className="w-4 h-4" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Continue with Google
            </Button>
            <Button variant="outline" className="w-full h-10 bg-white hover:bg-[#FAF8F3] border-[#E8E4DC] text-[#111111] font-bold text-sm rounded-xl gap-2.5">
              <svg viewBox="0 0 24 24" className="w-4 h-4" xmlns="http://www.w3.org/2000/svg">
                <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zm12.6 0H12.6V0H24v11.4z" fill="#00a4ef"/>
                <path d="M11.4 11.4H0V0h11.4v11.4z" fill="#f25022"/>
                <path d="M24 11.4H12.6V0H24v11.4z" fill="#7fba00"/>
                <path d="M11.4 24H0V12.6h11.4V24z" fill="#00a4ef"/>
                <path d="M24 24H12.6V12.6H24V24z" fill="#ffb900"/>
              </svg>
              Continue with Microsoft
            </Button>
          </div>

          <div className="relative flex items-center py-1.5 mb-5">
            <div className="flex-grow border-t border-[#E8E4DC]"></div>
            <span className="flex-shrink-0 mx-4 text-[#858585] text-[10px] font-bold uppercase tracking-widest">or</span>
            <div className="flex-grow border-t border-[#E8E4DC]"></div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            {!isLogin && (
              <div>
                <label className="block text-[11px] font-bold text-[#111111] mb-1 uppercase tracking-wide">Full name</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                    <svg className="h-4 w-4 text-[#858585]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <Input 
                    type="text" 
                    placeholder="John Doe" 
                    required 
                    value={name} 
                    onChange={e => setName(e.target.value)} 
                    className="h-10 pl-10 bg-white border-[#E8E4DC] focus-visible:ring-[#800020] focus-visible:border-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg shadow-sm"
                  />
                </div>
              </div>
            )}
            <div>
              <label className="block text-[11px] font-bold text-[#111111] mb-1 uppercase tracking-wide">Work email</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <svg className="h-4 w-4 text-[#858585]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <Input 
                  type="email" 
                  placeholder="you@company.com" 
                  required 
                  value={email} 
                  onChange={e => setEmail(e.target.value)} 
                  className="h-10 pl-10 bg-white border-[#E8E4DC] focus-visible:ring-[#800020] focus-visible:border-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg shadow-sm"
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="block text-[11px] font-bold text-[#111111] uppercase tracking-wide">Password</label>
                {isLogin && (
                  <button type="button" className="text-[10px] font-bold text-[#858585] hover:text-[#111111] transition-colors">Forgot?</button>
                )}
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <svg className="h-4 w-4 text-[#858585]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <Input 
                  type="password" 
                  placeholder={isLogin ? "Enter your password" : "Create a password"}
                  required 
                  value={password} 
                  onChange={e => setPassword(e.target.value)} 
                  className="h-10 pl-10 bg-white border-[#E8E4DC] focus-visible:ring-[#800020] focus-visible:border-[#800020] text-sm font-medium placeholder:text-[#858585] rounded-lg shadow-sm"
                />
                <button type="button" className="absolute inset-y-0 right-0 pr-3.5 flex items-center">
                  <svg className="h-4 w-4 text-[#858585] hover:text-[#111111]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
              </div>
            </div>

            {!isLogin && (
              <div className="flex items-center pt-1.5">
                <input type="checkbox" id="terms" required className="h-3.5 w-3.5 rounded border-[#E8E4DC] text-[#800020] focus:ring-[#800020] accent-[#800020]" />
                <label htmlFor="terms" className="ml-2 block text-xs font-medium text-[#5A5A5A]">
                  I agree to the <span className="font-bold text-[#111111]">Terms</span> and <span className="font-bold text-[#111111]">Privacy Policy</span>
                </label>
              </div>
            )}

            <Button type="submit" className="w-full h-11 mt-3 bg-[#111111] hover:bg-[#2A2A2A] text-white font-bold text-sm rounded-xl border-none shadow-md transition-all duration-200" disabled={loading}>
              {loading ? "Processing..." : (isLogin ? "Log In" : "Create account")} &rarr;
            </Button>
          </form>

          <p className="mt-6 text-center text-[13px] font-medium text-[#5A5A5A]">
            {isLogin ? "Don't have an account?" : "Already have an account?"}{' '}
            <button 
              type="button" 
              className="text-[#111111] hover:text-[#800020] font-bold transition-colors"
              onClick={() => setIsLogin(!isLogin)}
            >
              {isLogin ? "Create account" : "Log in"}
            </button>
          </p>
        </div>

        {/* Right Side: Visuals */}
        <div className="hidden md:flex w-[380px] lg:w-[400px] bg-[#FAF8F3] flex-col p-10 relative overflow-hidden shrink-0 border-l border-[#E8E4DC]">
          <div className="relative z-10 flex flex-col h-full">
            <div className="inline-flex px-3 py-1 bg-white/60 border border-[#E8E4DC] text-[#800020] text-[10px] uppercase tracking-wider font-bold rounded-full mb-6 backdrop-blur-sm self-start">
              AI Marketing Platform
            </div>

            <h3 className="text-[28px] font-bold text-[#111111] tracking-tight leading-[1.1] mb-8 pr-4">
              Turn insights into real growth.
            </h3>

            <div className="space-y-6 flex-1">
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-0.5">
                  <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-[#111111] font-bold text-[13px] mb-0.5">Your Brand, Smarter</h4>
                  <p className="text-[#5A5A5A] text-xs font-medium leading-relaxed pr-4">Access all your brand data, campaigns, and insights in one place.</p>
                </div>
              </div>

              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center shrink-0 mt-0.5">
                  <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-[#111111] font-bold text-[13px] mb-0.5">AI Agents at Your Service</h4>
                  <p className="text-[#5A5A5A] text-xs font-medium leading-relaxed pr-4">Continue where you left off with your AI marketing team.</p>
                </div>
              </div>

              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center shrink-0 mt-0.5">
                  <svg className="w-4 h-4 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-[#111111] font-bold text-[13px] mb-0.5">Real Business Impact</h4>
                  <p className="text-[#5A5A5A] text-xs font-medium leading-relaxed pr-4">Save time, reduce costs, and grow your brand with AI.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Abstract graphics behind text */}
          <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-gradient-to-bl from-[#F5E6E8] to-transparent opacity-60 rounded-full blur-[40px] -mr-20 -mt-20 pointer-events-none" />
          
          {/* Bottom overlapping cards graphic */}
          <div className="absolute -bottom-12 -right-12 w-[300px] h-[160px] bg-white rounded-tl-[24px] shadow-[0_-10px_40px_rgba(0,0,0,0.05)] border-t border-l border-[#E8E4DC] p-5 flex flex-col pointer-events-none transform -rotate-3">
             <div className="w-20 h-2.5 rounded-full bg-[#E8E4DC] mb-3" />
             <div className="w-full flex gap-2.5 mb-3">
               <div className="w-full h-12 rounded-lg bg-[#FAF8F3] border border-[#E8E4DC]" />
               <div className="w-full h-12 rounded-lg bg-[#FAF8F3] border border-[#E8E4DC]" />
             </div>
          </div>
        </div>
      </div>
    </div>
  )
}
