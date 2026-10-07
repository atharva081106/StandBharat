import os
from pathlib import Path

BASE_DIR = Path("frontend")

def write_file(path, content):
    full_path = BASE_DIR / path
    os.makedirs(full_path.parent, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# --- lib/utils.ts ---
utils_ts = """
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
"""
write_file("lib/utils.ts", utils_ts)

# --- components/ui/card.tsx ---
card_tsx = """
import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("rounded-lg border border-[#E5E5E5] bg-white text-gray-950 shadow-sm", className)} {...props} />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(({ className, ...props }, ref) => (
  <h3 ref={ref} className={cn("text-lg font-semibold leading-none tracking-tight", className)} {...props} />
))
CardTitle.displayName = "CardTitle"

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

export { Card, CardHeader, CardTitle, CardContent }
"""
write_file("components/ui/card.tsx", card_tsx)

# --- components/ui/button.tsx ---
button_tsx = """
import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "secondary"
  size?: "default" | "sm" | "lg"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant = "default", size = "default", ...props }, ref) => {
  const variants = {
    default: "bg-orange-500 text-white hover:bg-orange-600",
    outline: "border border-[#E5E5E5] bg-transparent hover:bg-gray-50 text-[#111111]",
    ghost: "hover:bg-gray-100 text-[#525252]",
    secondary: "bg-[#111111] text-white hover:bg-[#525252]"
  }
  const sizes = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
    lg: "h-11 rounded-md px-8"
  }
  return (
    <button ref={ref} className={cn("inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50", variants[variant], sizes[size], className)} {...props} />
  )
})
Button.displayName = "Button"
export { Button }
"""
write_file("components/ui/button.tsx", button_tsx)

# --- components/ui/badge.tsx ---
badge_tsx = """
import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "success" | "warning" | "danger"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "border-transparent bg-[#111111] text-white",
    secondary: "border-transparent bg-gray-100 text-[#525252]",
    outline: "text-[#525252]",
    success: "border-transparent bg-green-100 text-green-800",
    warning: "border-transparent bg-amber-100 text-amber-800",
    danger: "border-transparent bg-red-100 text-red-800"
  }
  return (
    <div className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors", variants[variant], className)} {...props} />
  )
}
export { Badge }
"""
write_file("components/ui/badge.tsx", badge_tsx)

# --- components/ui/input.tsx ---
input_tsx = """
import * as React from "react"
import { cn } from "@/lib/utils"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, type, ...props }, ref) => {
  return (
    <input
      type={type}
      className={cn(
        "flex h-10 w-full rounded-md border border-[#E5E5E5] bg-white px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-500 disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Input.displayName = "Input"
export { Input }
"""
write_file("components/ui/input.tsx", input_tsx)

# --- lib/mock/data.ts ---
mock_data_ts = """
export const DEMO_MODE = true;

export const mockUser = {
  id: "u_1",
  name: "Atharva",
  email: "demo@standbharat.ai",
  role: "OWNER"
};

export const mockWorkspaces = [
  { id: "w_1", name: "Acme Corp" }
];

export const mockBrands = [
  { id: "b_1", name: "Acme SaaS", workspace_id: "w_1" }
];

export const mockKPIs = {
  revenue: { value: "₹4.82L", change: "+18.4%" },
  leads: { value: "1,284", change: "+23.1%" },
  conversionRate: { value: "8.4%", change: "+2.1%" },
  aiSpend: { value: "₹2,410", change: "+8.2%" }
};

export const mockAgents = [
  { id: "analytics", name: "Analytics Agent", status: "ACTIVE", description: "Monitors performance metrics" },
  { id: "seo", name: "SEO Agent", status: "ACTIVE", description: "Optimizes content for search" },
  { id: "writer", name: "Writer Agent", status: "WAITING", description: "Generates long-form content" },
  { id: "growth", name: "Growth Agent", status: "IDLE", description: "Identifies growth opportunities" }
];

export const mockOpportunities = [
  { id: "o_1", title: "Improve organic conversion on 'Skincare Guide'", impact: "HIGH", confidence: "87%", effort: "MEDIUM", priority: 8.6, status: "NEW" },
  { id: "o_2", title: "Create LinkedIn campaign for Q4 launch", impact: "MEDIUM", confidence: "92%", effort: "LOW", priority: 7.2, status: "IN_PROGRESS" }
];

export const mockApprovals = [
  { id: "a_1", title: "Publish 'Top 10 SEO Trends'", agent: "Writer Agent", risk: "LOW", requested: "2 hours ago" },
  { id: "a_2", title: "Increase ad budget by ₹10,000", agent: "Campaign Agent", risk: "HIGH", requested: "5 hours ago" }
];

export const mockContent = [
  { id: "c_1", title: "Top 10 SEO Trends in 2026", type: "Blog", status: "DRAFT", author: "Writer Agent", updated: "1 hour ago" },
  { id: "c_2", title: "Q4 Product Launch Thread", type: "X Thread", status: "PUBLISHED", author: "Social Agent", updated: "1 day ago" }
];
"""
write_file("lib/mock/data.ts", mock_data_ts)

# --- lib/providers/MockProvider.tsx ---
mock_provider_tsx = """
"use client"
import React, { createContext, useContext, useState, useEffect } from 'react';
import { mockUser, mockWorkspaces, mockBrands } from '../mock/data';

type AuthState = 'loggedOut' | 'loggedIn' | 'onboarding' | 'onboardingComplete';

interface AuthContextType {
  authState: AuthState;
  setAuthState: (state: AuthState) => void;
  user: typeof mockUser | null;
  activeWorkspace: typeof mockWorkspaces[0] | null;
  activeBrand: typeof mockBrands[0] | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>('loggedOut');
  const [user, setUser] = useState<typeof mockUser | null>(null);
  
  useEffect(() => {
    if (authState === 'loggedIn' || authState === 'onboardingComplete') {
      setUser(mockUser);
    } else {
      setUser(null);
    }
  }, [authState]);

  return (
    <AuthContext.Provider value={{
      authState, setAuthState, user, activeWorkspace: mockWorkspaces[0], activeBrand: mockBrands[0]
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
"""
write_file("lib/providers/MockProvider.tsx", mock_provider_tsx)

print("Core UI components and Mock providers generated.")
