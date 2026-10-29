import * as React from "react"
import { Inbox } from "lucide-react"
import { cn } from "@/lib/utils"

export interface EmptyStateProps {
  title: string
  description?: string
  icon?: React.ComponentType<{ className?: string }>
  action?: React.ReactNode
  className?: string
}

export function EmptyState({
  title,
  description,
  icon: Icon = Inbox,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex min-h-[220px] w-full flex-col items-center justify-center p-6 text-center transition-colors",
        className
      )}
      role="region"
      aria-label={title}
    >
      <div className="flex size-9 items-center justify-center rounded-[8px] border border-border bg-muted/60 text-muted-foreground shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
        <Icon className="size-4 text-muted-foreground" />
      </div>
      <h3 className="mt-3 text-sm font-semibold tracking-tight text-foreground">
        {title}
      </h3>
      {description && (
        <p className="mt-1.5 max-w-sm text-xs leading-relaxed text-muted-foreground">
          {description}
        </p>
      )}
      {action && <div className="mt-3.5 flex items-center gap-2">{action}</div>}
    </div>
  )
}
