"use client"

import * as React from "react"
import Link from "next/link"
import { AlertTriangle, ShieldCheck, ArrowRight } from "lucide-react"

import type { AtRiskTask } from "@/types"
import { PriorityBadge } from "@/components/tasks/priority-badge"
import { StatusBadge } from "@/components/tasks/status-badge"
import { DeadlineIndicator } from "@/components/tasks/deadline-indicator"
import { EmptyState } from "@/components/common/empty-state"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface AtRiskTasksProps {
  atRiskTasks?: AtRiskTask[]
  isLoading?: boolean
  className?: string
}

export function AtRiskTasks({
  atRiskTasks = [],
  isLoading = false,
  className,
}: AtRiskTasksProps) {
  if (isLoading) {
    return (
      <div
        className={cn(
          "flex flex-col rounded-lg border border-border bg-card p-5 shadow-2xs animate-pulse",
          className
        )}
      >
        <div className="flex items-center justify-between pb-4">
          <div className="h-5 w-32 rounded bg-muted/70" />
          <div className="h-4 w-12 rounded bg-muted/50" />
        </div>
        <div className="space-y-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <div
              key={i}
              className="flex flex-col gap-2 rounded-md border border-border p-3"
            >
              <div className="h-4 w-40 rounded bg-muted/70" />
              <div className="h-3 w-64 rounded bg-muted/50" />
            </div>
          ))}
        </div>
      </div>
    )
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
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold tracking-tight text-foreground">
            At-Risk Tasks
          </h3>
          {atRiskTasks.length > 0 && (
            <Badge
              variant="outline"
              className="border-red-200 bg-red-50 text-red-700 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-400 text-[10px] px-1.5 py-0"
            >
              {atRiskTasks.length} Flagged
            </Badge>
          )}
        </div>
        <p className="text-xs text-muted-foreground hidden sm:block">
          Tasks requiring adaptive intervention
        </p>
      </div>

      {/* List or Empty State */}
      {atRiskTasks.length === 0 ? (
        <div className="pt-4">
          <EmptyState
            icon={ShieldCheck}
            title="No at-risk tasks"
            description="All scheduled workloads are within safe buffers and deadlines are on track."
            className="min-h-[180px] p-4"
          />
        </div>
      ) : (
        <div className="divide-y divide-border/60">
          {atRiskTasks.map(({ task, riskLevel, riskReason }) => (
            <div
              key={task.id}
              className="flex flex-col gap-2 py-3.5 first:pt-3.5 last:pb-1"
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5">
                <div className="flex items-center gap-2 min-w-0">
                  <Link
                    href={`/tasks/${task.id}`}
                    className="truncate text-sm font-medium text-foreground hover:text-primary transition-colors"
                  >
                    {task.title}
                  </Link>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <PriorityBadge priority={task.priority} />
                  <StatusBadge status={task.status} />
                </div>
              </div>

              {/* Risk Alert Callout */}
              <div
                className={cn(
                  "flex items-start gap-2 rounded-md border p-2.5 text-xs leading-relaxed",
                  riskLevel === "critical"
                    ? "border-red-200/80 bg-red-50/60 text-red-800 dark:border-red-900/40 dark:bg-red-950/30 dark:text-red-300"
                    : "border-orange-200/80 bg-orange-50/60 text-orange-800 dark:border-orange-900/40 dark:bg-orange-950/30 dark:text-orange-300"
                )}
              >
                <AlertTriangle
                  className={cn(
                    "size-3.5 shrink-0 mt-0.5",
                    riskLevel === "critical" ? "text-red-600 dark:text-red-400" : "text-orange-600 dark:text-orange-400"
                  )}
                />
                <div className="flex-1">
                  <span className="font-semibold uppercase tracking-wider text-[10px] mr-1.5">
                    {riskLevel} Risk:
                  </span>
                  <span>{riskReason}</span>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-muted-foreground pt-0.5">
                <DeadlineIndicator deadline={task.deadline} />
                <Link
                  href={`/tasks/${task.id}`}
                  className="inline-flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
                >
                  <span>Resolve in Task View</span>
                  <ArrowRight className="size-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
