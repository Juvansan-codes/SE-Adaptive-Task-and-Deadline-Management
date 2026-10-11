"use client"

import * as React from "react"
import Link from "next/link"
import {
  CheckCircle2,
  AlertTriangle,
  PlayCircle,
  Clock,
  Sparkles,
  ArrowRight,
  Circle,
} from "lucide-react"

import type { ScheduleItem } from "@/types"
import { Badge } from "@/components/ui/badge"
import { PriorityBadge } from "@/components/tasks/priority-badge"
import { cn } from "@/lib/utils"

interface TimelineItemProps {
  item: ScheduleItem
  isLast?: boolean
  className?: string
}

export function TimelineItem({
  item,
  isLast = false,
  className,
}: TimelineItemProps) {
  const isCompleted = item.status === "completed"
  const isOverdue = item.status === "overdue"
  const isInProgress = item.status === "in_progress"
  const isRecommended = item.isRecommended

  const formatDuration = (mins: number) => {
    if (mins >= 60) {
      const hours = Math.floor(mins / 60)
      const remainingMins = mins % 60
      return remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
    }
    return `${mins}m`
  }

  // Determine state icon and status styling
  const renderStatusIndicator = () => {
    if (isCompleted) {
      return (
        <div className="flex size-7 items-center justify-center rounded-full border border-emerald-300 bg-emerald-50 text-emerald-600 dark:border-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-400">
          <CheckCircle2 className="size-4" />
        </div>
      )
    }

    if (isOverdue) {
      return (
        <div className="flex size-7 items-center justify-center rounded-full border border-red-300 bg-red-50 text-red-600 dark:border-red-800 dark:bg-red-950/60 dark:text-red-400">
          <AlertTriangle className="size-4" />
        </div>
      )
    }

    if (isRecommended || isInProgress) {
      return (
        <div className="flex size-7 items-center justify-center rounded-full border border-orange-400 bg-orange-50 text-orange-600 dark:border-orange-800 dark:bg-orange-950/60 dark:text-orange-400">
          <PlayCircle className="size-4" />
        </div>
      )
    }

    return (
      <div className="flex size-7 items-center justify-center rounded-full border border-border bg-muted/60 text-muted-foreground">
        <Circle className="size-3 fill-muted-foreground/40" />
      </div>
    )
  }

  return (
    <div
      id={item.id}
      className={cn("relative flex gap-4 sm:gap-6", className)}
    >
      {/* Left Column: Time & Duration Indicator */}
      <div className="flex w-24 sm:w-28 flex-col items-end pt-1 shrink-0 text-right">
        <span
          className={cn(
            "text-xs sm:text-sm font-semibold tracking-tight tabular-nums",
            isOverdue
              ? "text-red-600 dark:text-red-400"
              : isCompleted
              ? "text-muted-foreground"
              : "text-foreground"
          )}
        >
          {item.startTime}
        </span>
        <span className="text-[11px] text-muted-foreground tabular-nums">
          {item.endTime}
        </span>
        <span className="mt-1 inline-flex items-center gap-1 rounded bg-muted/50 px-1.5 py-0.5 text-[10px] text-muted-foreground tabular-nums">
          <Clock className="size-2.5" />
          <span>{formatDuration(item.durationMinutes)}</span>
        </span>
      </div>

      {/* Middle Column: Vertical Timeline Connector */}
      <div className="relative flex flex-col items-center">
        {renderStatusIndicator()}
        {!isLast && (
          <div className="my-1.5 w-[2px] flex-1 bg-border/80 transition-colors" />
        )}
      </div>

      {/* Right Column: Schedule Item Card */}
      <div
        className={cn(
          "flex-1 pb-6",
          isLast && "pb-0"
        )}
      >
        <div
          className={cn(
            "group relative flex flex-col rounded-lg border border-border bg-card p-4 sm:p-5 shadow-2xs transition-colors hover:border-neutral-300 dark:hover:border-neutral-700",
            isRecommended &&
              "border-orange-500/40 bg-orange-500/[0.02] dark:border-orange-500/30",
            isCompleted &&
              "opacity-85 bg-neutral-50/40 dark:bg-neutral-900/30",
            isOverdue &&
              "border-red-300/80 bg-red-50/20 dark:border-red-900/40 dark:bg-red-950/20"
          )}
        >
          {/* Header Badges & Category */}
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              {isRecommended && (
                <Badge
                  variant="outline"
                  className="border-orange-500/40 bg-orange-500/10 text-orange-600 dark:text-orange-400 text-[10px] font-semibold uppercase tracking-wider"
                >
                  RECOMMENDED NEXT
                </Badge>
              )}
              {isCompleted && (
                <Badge
                  variant="outline"
                  className="border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900/50 dark:bg-emerald-950/40 dark:text-emerald-400 text-[10px]"
                >
                  Completed
                </Badge>
              )}
              {isOverdue && (
                <Badge
                  variant="outline"
                  className="border-red-200 bg-red-50 text-red-700 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-400 text-[10px] font-medium"
                >
                  Overdue
                </Badge>
              )}
              {isInProgress && !isRecommended && (
                <Badge
                  variant="outline"
                  className="border-orange-200 bg-orange-50 text-orange-700 dark:border-orange-900/50 dark:bg-orange-950/40 dark:text-orange-400 text-[10px]"
                >
                  In Progress
                </Badge>
              )}
              <span className="text-xs text-muted-foreground font-medium">
                {item.category}
              </span>
            </div>

            {item.priority && <PriorityBadge priority={item.priority} />}
          </div>

          {/* Title & Link */}
          <div className="mt-2.5">
            {item.taskId ? (
              <Link
                href={`/tasks/${item.taskId}`}
                className={cn(
                  "text-sm sm:text-base font-semibold tracking-tight transition-colors hover:text-primary",
                  isCompleted ? "text-foreground/90 line-through decoration-muted-foreground/40" : "text-foreground"
                )}
              >
                {item.title}
              </Link>
            ) : (
              <h4
                className={cn(
                  "text-sm sm:text-base font-semibold tracking-tight text-foreground",
                  isCompleted && "line-through decoration-muted-foreground/40 text-foreground/90"
                )}
              >
                {item.title}
              </h4>
            )}
          </div>

          {/* Recommended Reason Box */}
          {isRecommended && item.recommendationReason && (
            <div className="mt-3 flex items-start gap-2 rounded-md border border-orange-200/60 bg-orange-50/50 p-2.5 text-xs text-orange-950 dark:border-orange-900/30 dark:bg-orange-950/30 dark:text-orange-300">
              <Sparkles className="size-3.5 shrink-0 text-orange-500 mt-0.5" />
              <div className="flex-1 leading-relaxed">
                <span className="font-semibold uppercase tracking-wider text-[10px] mr-1.5">
                  Adaptive Focus:
                </span>
                <span>{item.recommendationReason}</span>
              </div>
            </div>
          )}

          {/* Overdue Warning Callout */}
          {isOverdue && item.notes && (
            <div className="mt-3 flex items-start gap-2 rounded-md border border-red-200/60 bg-red-50/50 p-2.5 text-xs text-red-950 dark:border-red-900/30 dark:bg-red-950/30 dark:text-red-300">
              <AlertTriangle className="size-3.5 shrink-0 text-red-500 mt-0.5" />
              <div className="flex-1 leading-relaxed">
                <span className="font-semibold uppercase tracking-wider text-[10px] mr-1.5">
                  Rescheduled:
                </span>
                <span>{item.notes}</span>
              </div>
            </div>
          )}

          {/* General Notes */}
          {!isRecommended && !isOverdue && item.notes && (
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              {item.notes}
            </p>
          )}

          {/* Task Link Footer if taskId is available */}
          {item.taskId && (
            <div className="mt-3.5 flex items-center justify-between border-t border-border/50 pt-2 text-xs text-muted-foreground">
              <span className="text-[11px]">Task reference: #{item.taskId}</span>
              <Link
                href={`/tasks/${item.taskId}`}
                className="inline-flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
              >
                <span>View Details</span>
                <ArrowRight className="size-3" />
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
