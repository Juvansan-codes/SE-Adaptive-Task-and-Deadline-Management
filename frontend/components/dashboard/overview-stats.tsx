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
          "grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5",
          className
        )}
      >
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="flex flex-col justify-between rounded-lg border border-border bg-card p-4 shadow-2xs animate-pulse"
          >
            <div className="h-3 w-20 rounded bg-muted/60" />
            <div className="my-2 h-7 w-16 rounded bg-muted/70" />
            <div className="h-2.5 w-24 rounded bg-muted/40" />
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
        "grid grid-cols-1 min-[340px]:grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5",
        className
      )}
    >
      {stats.map((item) => {
        const Icon = item.icon
        return (
          <div
            key={item.id}
            className={cn(
              "flex flex-col justify-between rounded-lg border border-border bg-card p-3.5 shadow-2xs transition-colors",
              item.alert &&
                "border-orange-500/30 bg-orange-500/[0.02] dark:border-orange-500/20"
            )}
          >
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground/80">
                {item.label}
              </span>
              <Icon
                className={cn(
                  "size-3.5 shrink-0",
                  item.alert ? "text-orange-600 dark:text-orange-400" : "text-muted-foreground/60"
                )}
              />
            </div>
            <div className="my-1.5 flex items-baseline gap-1.5">
              <span
                className={cn(
                  "text-2xl font-bold tracking-tight text-foreground",
                  item.alert && "text-orange-600 dark:text-orange-400"
                )}
              >
                {item.value}
              </span>
            </div>
            <p className="text-[11px] text-muted-foreground truncate">
              {item.context}
            </p>
          </div>
        )
      })}
    </div>
  )
}
