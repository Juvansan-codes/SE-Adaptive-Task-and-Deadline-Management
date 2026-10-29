"use client"

import * as React from "react"
import { Calendar } from "lucide-react"

import type { DaySchedule } from "@/types"
import { TimelineItem } from "./timeline-item"
import { EmptyState } from "@/components/common/empty-state"
import { cn } from "@/lib/utils"

interface TimelineViewProps {
  schedule: DaySchedule
  className?: string
}

export function TimelineView({ schedule, className }: TimelineViewProps) {
  const { items } = schedule

  if (items.length === 0) {
    return (
      <div className={cn("rounded-[10px] border border-border bg-card p-6 shadow-[0_1px_2px_rgba(0,0,0,0.03)]", className)}>
        <EmptyState
          icon={Calendar}
          title="No scheduled items for this date"
          description="Your adaptive timeline will automatically populate focus blocks as tasks are scheduled."
        />
      </div>
    )
  }

  const completedCount = items.filter((i) => i.status === "completed").length
  const pendingCount = items.filter((i) => i.status === "pending" || i.status === "in_progress").length
  const overdueCount = items.filter((i) => i.status === "overdue").length

  return (
    <div
      id="schedule-timeline"
      className={cn(
        "flex flex-col rounded-[10px] border border-border bg-card p-5 sm:p-6 shadow-[0_1px_2px_rgba(0,0,0,0.03)]",
        className
      )}
    >
      {/* Schedule Meta Sub-bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/70 pb-3.5 mb-5">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Day Schedule
          </span>
          <span className="text-xs text-muted-foreground">•</span>
          <span className="text-xs text-foreground font-medium">
            {items.length} focus sessions
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
          <span className="text-emerald-600 dark:text-emerald-400 font-medium font-mono tabular-nums">
            {completedCount} completed
          </span>
          <span>•</span>
          <span className="font-mono tabular-nums">{pendingCount} remaining</span>
          {overdueCount > 0 && (
            <>
              <span>•</span>
              <span className="text-red-600 dark:text-red-400 font-medium font-mono tabular-nums">
                {overdueCount} overdue
              </span>
            </>
          )}
        </div>
      </div>

      {/* Timeline items list */}
      <div className="flex flex-col">
        {items.map((item, index) => (
          <TimelineItem
            key={item.id}
            item={item}
            isLast={index === items.length - 1}
          />
        ))}
      </div>
    </div>
  )
}
