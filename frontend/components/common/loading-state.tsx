import * as React from "react"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

export interface LoadingStateProps {
  message?: string
  description?: string
  className?: string
  size?: "sm" | "default" | "lg"
}

export function LoadingState({
  message = "Loading...",
  description,
  className,
  size = "default",
}: LoadingStateProps) {
  const iconSizes = {
    sm: "size-4",
    default: "size-5",
    lg: "size-7",
  }

  return (
    <div
      suppressHydrationWarning
      className={cn(
        "flex min-h-[200px] w-full flex-col items-center justify-center p-6 text-center",
        className
      )}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <Loader2
        className={cn(
          "animate-spin text-primary motion-reduce:animate-none",
          iconSizes[size]
        )}
      />
      {message && (
        <p className="mt-3 text-sm font-medium text-foreground">{message}</p>
      )}
      {description && (
        <p className="mt-1 text-xs text-muted-foreground">{description}</p>
      )}
      <span className="sr-only">{message}</span>
    </div>
  )
}
