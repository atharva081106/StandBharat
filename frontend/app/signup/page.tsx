"use client"
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function SignupPage() {
  const router = useRouter()
  
  useEffect(() => {
    // Open the auth modal for signup
    window.dispatchEvent(new Event('open-auth-signup'))
    // Redirect the background to the home page so they aren't on a blank page
    router.push('/')
  }, [router])
  
  return null
}
