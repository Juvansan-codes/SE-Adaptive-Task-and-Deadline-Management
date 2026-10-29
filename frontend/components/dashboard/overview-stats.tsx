"use client"

import * as React from "react"
import { Clock, CalendarClock, TrendingUp, ListTodo, AlertTriangle } from "lucide-react"
import type { DashboardOverview } from "@/types"
import { cn } from "@/lib/utils"

interface OverviewStatsProps {
  overview?: DashboardOverview
  isLoading?: boolean
  className?: string
}

export function OverviewStats({
  overview,
  isLoading = false,
  className,
}: OverviewStatsProps) {
  if (isLoading || !overview) {
    return (
      <div
        className={cn(
          "grid grid-cols-1 min-[480px]:grid-cols-2 lg:grid-cols-5 gap-4",
          className
        )}
      >
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="flex flex-col justify-between rounded-[10px] border border-border bg-card p-4 shadow-[0_1px_2px_rgba(0,0,0,0.03)] animate-pulse"
          >
            <div className="flex items-center justify-between">
              <div className="h-3 w-20 rounded bg-muted/70" />
              <div className="size-3.5 rounded bg-muted/60" />
            </div>
            <div className="mt-2 h-7 w-16 rounded bg-muted/80" />
            <div className="mt-2 h-3 w-24 rounded bg-muted/50" />
          </div>
        ))}
      </div>
    )
  }

  const stats = [
    {
      id: "available",
      label: "Available Today",
      value: `${overview.availableTimeHours.toFixed(1)}h`,
      context: "6.0h focus capacity",
      icon: Clock,
      alert: false,
    },
    {
      id: "workload",
      label: "Today's Workload",
      value: `${overview.scheduledWorkloadHours.toFixed(1)}h`,
      context: "4 scheduled sessions",
      icon: CalendarClock,
      alert: false,
    },
    {
      id: "progress",
      label: "Overall Progress",
      value: `${overview.overallProgress}%`,
      context: "Workload completion",
      icon: TrendingUp,
      alert: false,
    },
    {
      id: "pending",
      label: "Pending Tasks",
      value: `${overview.pendingTasksCount}`,
      context: `${overview.completedTodayCount} done today`,
      icon: ListTodo,
      alert: false,
    },
    {
      id: "at-risk",
      label: "At-Risk Tasks",
      value: `${overview.atRiskTasksCount}`,
      context:
        overview.atRiskTasksCount > 0 ? "Requires review" : "All on schedule",
      icon: AlertTriangle,
      alert: overview.atRiskTasksCount > 0,
    },
  ]

  return (
    <div
      className={cn(
        "grid grid-cols-1 min-[480px]:grid-cols-2 lg:grid-cols-5 gap-4",
        className
      )}
    >
      {stats.map((item) => {
        const Icon = item.icon
        return (
          <div
            key={item.id}
            className={cn(
              "flex flex-col justify-between rounded-[10px] border border-border bg-card p-4 shadow-[0_1px_2px_rgba(0,0,0,0.03)] transition-colors",
              item.alert &&
                "border-orange-500/30 bg-orange-500/[0.02] dark:border-orange-500/20"
            )}
          >
            {/* Top row: micro-icon and uppercase label (flex-between) */}
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-[12px] font-semibold uppercase tracking-[0.06em] text-muted-foreground">
                {item.label}
              </span>
              <Icon
                className={cn(
                  "size-3.5 shrink-0",
                  item.alert ? "text-orange-600 dark:text-orange-400" : "text-muted-foreground/60"
                )}
              />
            </div>

            {/* Middle: large tabular number (mt-2 text-[28px] font-bold tabular-nums) */}
            <div className="mt-2 flex items-baseline">
              <span
                className={cn(
                  "text-[28px] font-bold font-mono tabular-nums leading-none tracking-tight text-foreground",
                  item.alert && "text-orange-600 dark:text-orange-400"
                )}
              >
                {item.value}
              </span>
            </div>

            {/* Bottom: sub-metric pill/text (mt-1 / mt-2) */}
            <div className="mt-2 text-xs text-muted-foreground truncate">
              {item.context}
            </div>
          </div>
        )
      })}
    </div>
  )
}
