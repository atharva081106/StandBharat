import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "success" | "warning" | "danger"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "border-transparent bg-[var(--color-bg-subtle)] text-[var(--color-text-primary)]",
    secondary: "border-transparent bg-[var(--color-bg-subtle)] text-[var(--color-text-tertiary)]",
    outline: "border-[var(--color-border-primary)] text-[var(--color-text-tertiary)]",
    success: "border-transparent bg-green-50 text-green-700",
    warning: "border-transparent bg-amber-50 text-amber-700",
    danger: "border-transparent bg-red-50 text-red-700"
  }
  return (
    <div className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors", variants[variant], className)} {...props} />
  )
}
export { Badge }
