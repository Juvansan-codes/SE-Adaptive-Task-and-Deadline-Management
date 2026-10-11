import * as React from "react"
import { AlertCircle, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export interface ErrorStateProps {
  title?: string
  message: string
  onRetry?: () => void
  action?: React.ReactNode
  className?: string
}

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
  action,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "flex min-h-[220px] w-full flex-col items-center justify-center rounded-lg border border-destructive/20 bg-destructive/5 p-6 text-center transition-colors",
        className
      )}
      role="alert"
    >
      <div className="flex size-10 items-center justify-center rounded-md border border-destructive/20 bg-background text-destructive shadow-2xs">
        <AlertCircle className="size-5" />
      </div>
      <h3 className="mt-3 text-sm font-semibold tracking-tight text-foreground">
        {title}
      </h3>
      <p className="mt-1 max-w-sm text-xs leading-relaxed text-muted-foreground">
        {message}
      </p>
      <div className="mt-4 flex items-center gap-2">
        {onRetry && (
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            className="border-destructive/30 hover:bg-destructive/10"
          >
            <RotateCcw className="size-3.5" />
            Try again
          </Button>
        )}
        {action}
      </div>
    </div>
  )
}
