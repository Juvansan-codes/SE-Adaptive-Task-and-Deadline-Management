"use client"

import * as React from "react"
import Link from "next/link"
import { Calendar, CheckCircle2, PlayCircle, Circle, ArrowRight } from "lucide-react"

import type { ScheduleBlock } from "@/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/common/empty-state"
import { cn } from "@/lib/utils"

interface TodayScheduleProps {
  schedule?: ScheduleBlock[]
  isLoading?: boolean
  className?: string
}

export function TodaySchedule({
  schedule = [],
  isLoading = false,
  className,
}: TodayScheduleProps) {
  if (isLoading) {
    return (
      <div
        className={cn(
          "flex flex-col rounded-lg border border-border bg-card p-5 shadow-2xs animate-pulse",
          className
        )}
      >
        <div className="flex items-center justify-between pb-4">
          <div className="h-5 w-28 rounded bg-muted/70" />
          <div className="h-4 w-16 rounded bg-muted/50" />
        </div>
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-3 rounded-md border border-border p-3"
            >
              <div className="h-8 w-16 rounded bg-muted/60" />
              <div className="space-y-1.5 flex-1">
                <div className="h-4 w-3/4 rounded bg-muted/70" />
                <div className="h-3 w-1/3 rounded bg-muted/40" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const getStatusConfig = (status: ScheduleBlock["status"]) => {
    switch (status) {
      case "completed":
        return {
          icon: CheckCircle2,
          badge: "Completed",
          badgeStyle: "border-neutral-200 bg-neutral-100 text-neutral-600 dark:border-neutral-800 dark:bg-neutral-800 dark:text-neutral-400",
          itemStyle: "opacity-75",
        }
      case "current":
        return {
          icon: PlayCircle,
          badge: "Active Now",
          badgeStyle: "border-orange-200 bg-orange-50 text-orange-700 dark:border-orange-900/50 dark:bg-orange-950/40 dark:text-orange-400 font-semibold",
          itemStyle: "border-orange-500/40 bg-orange-500/[0.03]",
        }
      case "upcoming":
      default:
        return {
          icon: Circle,
          badge: "Upcoming",
          badgeStyle: "border-neutral-200 bg-background text-neutral-600 dark:border-neutral-800 dark:text-neutral-400",
          itemStyle: "",
        }
    }
  }

  return (
    <div
      className={cn(
        "flex flex-col rounded-lg border border-border bg-card p-5 shadow-2xs",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-3.5 border-b border-border/70">
        <div>
          <h3 className="text-sm font-semibold tracking-tight text-foreground">
            Today&apos;s Schedule
          </h3>
          <p className="text-xs text-muted-foreground">
            Dynamic focus blocks for today
          </p>
        </div>
        <Link href="/schedule">
          <Button variant="ghost" size="sm" className="h-8 gap-1 text-xs">
            <span>Schedule</span>
            <ArrowRight className="size-3" />
          </Button>
        </Link>
      </div>

      {/* Schedule Items or Empty State */}
      {schedule.length === 0 ? (
        <div className="pt-4">
          <EmptyState
            icon={Calendar}
            title="No schedule blocks"
            description="No active schedule sessions allocated for today."
            className="min-h-[180px] p-4"
          />
        </div>
      ) : (
        <div className="mt-3.5 flex flex-col gap-2.5">
          {schedule.map((item) => {
            const config = getStatusConfig(item.status)
            const StatusIcon = config.icon

            return (
              <div
                key={item.id}
                className={cn(
                  "flex items-start gap-3 rounded-md border border-border/70 bg-card p-3 transition-colors hover:border-neutral-300 dark:hover:border-neutral-700",
                  config.itemStyle
                )}
              >
                {/* Time Indicator */}
                <div className="flex flex-col items-center justify-center rounded border border-border bg-muted/40 px-2 py-1 text-center shrink-0 w-20">
                  <span className="text-[11px] font-semibold tracking-tight text-foreground tabular-nums">
                    {item.startTime}
                  </span>
                  <span className="text-[10px] text-muted-foreground tabular-nums">
                    {item.endTime}
                  </span>
                </div>

                {/* Task Details */}
                <div className="flex flex-col min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-1.5">
                    {item.taskId ? (
                      <Link
                        href={`/tasks/${item.taskId}`}
                        className="truncate text-xs font-semibold text-foreground hover:text-primary transition-colors"
                      >
                        {item.title}
                      </Link>
                    ) : (
                      <span className="truncate text-xs font-semibold text-foreground">
                        {item.title}
                      </span>
                    )}
                  </div>
                  <div className="mt-1 flex items-center justify-between gap-2 text-[11px] text-muted-foreground">
                    <span className="truncate">{item.category}</span>
                    <Badge
                      variant="outline"
                      className={cn(
                        "inline-flex items-center gap-1 text-[10px] px-1.5 py-0 shrink-0",
                        config.badgeStyle
                      )}
                    >
                      <StatusIcon className="size-2.5" />
                      <span>{config.badge}</span>
                    </Badge>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
