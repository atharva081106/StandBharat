"use client"
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const router = useRouter()
  
  useEffect(() => {
    // Open the auth modal for login
    window.dispatchEvent(new Event('open-auth-login'))
    // Redirect the background to the home page so they aren't on a blank page
    router.push('/')
  }, [router])
  
  return null
}
