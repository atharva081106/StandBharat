import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "secondary" | "destructive"
  size?: "default" | "sm" | "lg"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant = "default", size = "default", ...props }, ref) => {
  const variants = {
    default: "bg-[var(--color-brand-accent)] text-white hover:bg-[var(--color-brand-accent-hover)] shadow-sm",
    outline: "border border-[var(--color-border-primary)] bg-transparent hover:bg-[var(--color-bg-subtle)] text-[var(--color-text-primary)] shadow-sm",
    ghost: "hover:bg-[var(--color-bg-subtle)] text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)]",
    secondary: "bg-[var(--color-bg-subtle)] text-[var(--color-text-primary)] hover:bg-[var(--color-border-primary)] shadow-sm",
    destructive: "bg-red-50 text-red-600 hover:bg-red-100 border border-red-200"
  }
  const sizes = {
    default: "h-9 px-4 py-2",
    sm: "h-8 rounded-md px-3 text-xs",
    lg: "h-10 rounded-md px-8"
  }
  return (
    <button ref={ref} className={cn("inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]", variants[variant], sizes[size], className)} {...props} />
  )
})
Button.displayName = "Button"
export { Button }
