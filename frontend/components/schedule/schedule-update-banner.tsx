"use client"

import * as React from "react"
import { Sparkles, ArrowDown, X } from "lucide-react"

import type { ScheduleUpdate } from "@/types"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface ScheduleUpdateBannerProps {
  update: ScheduleUpdate
  onViewSchedule?: () => void
  onDismiss?: () => void
  className?: string
}

export function ScheduleUpdateBanner({
  update,
  onViewSchedule,
  onDismiss,
  className,
}: ScheduleUpdateBannerProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        "relative flex flex-col gap-3 rounded-lg border border-orange-500/30 bg-orange-500/[0.03] p-4 text-foreground shadow-2xs transition-colors dark:border-orange-500/20 sm:flex-row sm:items-center sm:justify-between sm:p-4.5",
        className
      )}
    >
      <div className="flex items-start gap-3">
        <div className="flex size-8 shrink-0 items-center justify-center rounded-md border border-orange-500/30 bg-orange-500/10 text-orange-600 dark:text-orange-400">
          <Sparkles className="size-4" />
        </div>
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-semibold tracking-tight text-foreground">
              {update.title}
            </h4>
            <span className="text-[11px] text-muted-foreground">
              • {update.timestamp}
            </span>
          </div>

          {update.summary && (
            <p className="text-xs text-muted-foreground leading-relaxed">
              {update.summary}
            </p>
          )}

          <ul className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-foreground/90 font-medium">
            {update.changes.map((change, index) => (
              <li key={index} className="flex items-center gap-1.5">
                <span className="size-1 rounded-full bg-orange-500 shrink-0" />
                <span>{change}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0 pt-1 sm:pt-0">
        <Button
          variant="outline"
          size="sm"
          onClick={onViewSchedule}
          className="border-orange-500/30 text-xs hover:bg-orange-500/10 hover:text-orange-600 dark:hover:text-orange-400 gap-1.5"
        >
          <span>{update.recommendedAction || "View Updated Schedule"}</span>
          <ArrowDown className="size-3" />
        </Button>
        {onDismiss && (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onDismiss}
            className="size-8 text-muted-foreground hover:text-foreground"
            aria-label="Dismiss notification"
          >
            <X className="size-3.5" />
          </Button>
        )}
      </div>
    </div>
  )
}
