"use client"

import * as React from "react"
import Link from "next/link"
import { Play, ArrowRight, Sparkles, CheckCircle2, Clock } from "lucide-react"
import { toast } from "sonner"
import { useQueryClient } from "@tanstack/react-query"

import type { RecommendedTask as RecommendedTaskType } from "@/types"
import { PriorityBadge } from "@/components/tasks/priority-badge"
import { DeadlineIndicator } from "@/components/tasks/deadline-indicator"
import { StatusBadge } from "@/components/tasks/status-badge"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { EmptyState } from "@/components/common/empty-state"
import { useUpdateTaskStatus, TASK_KEYS } from "@/hooks/use-tasks"
import { DASHBOARD_KEYS } from "@/hooks/use-dashboard"
import { cn } from "@/lib/utils"

interface RecommendedTaskProps {
  recommended?: RecommendedTaskType | null
  isLoading?: boolean
  className?: string
}

export function RecommendedTask({
  recommended,
  isLoading = false,
  className,
}: RecommendedTaskProps) {
  const queryClient = useQueryClient()
  const updateStatusMutation = useUpdateTaskStatus()
  const [isStarting, setIsStarting] = React.useState(false)

  if (isLoading) {
    return (
      <div
        className={cn(
          "flex flex-col gap-4 rounded-lg border border-border bg-card p-6 shadow-2xs animate-pulse",
          className
        )}
      >
        <div className="flex items-center justify-between">
          <div className="h-5 w-36 rounded bg-muted/70" />
          <div className="h-5 w-20 rounded bg-muted/60" />
        </div>
        <div className="h-7 w-3/4 rounded bg-muted/80" />
        <div className="h-16 w-full rounded bg-muted/40" />
        <div className="flex gap-2 pt-2">
          <div className="h-9 w-28 rounded bg-muted/70" />
          <div className="h-9 w-24 rounded bg-muted/50" />
        </div>
      </div>
    )
  }

  if (!recommended || !recommended.task) {
    return (
      <div className={cn("rounded-lg border border-border bg-card p-6 shadow-2xs", className)}>
        <EmptyState
          icon={CheckCircle2}
          title="No recommended task"
          description="All high-priority workloads and imminent deadlines are currently on schedule."
          action={
            <Link href="/tasks">
              <Button variant="outline" size="sm">
                Browse All Tasks
              </Button>
            </Link>
          }
        />
      </div>
    )
  }

  const { task, recommendationReason, urgencyLabel } = recommended
  const isInProgress = task.status === "in_progress"
  const isCompleted = task.status === "completed"

  const handleStartTask = async () => {
    if (isInProgress) return
    setIsStarting(true)
    try {
      await updateStatusMutation.mutateAsync({
        id: task.id,
        status: "in_progress",
      })
      queryClient.invalidateQueries({ queryKey: DASHBOARD_KEYS.all })
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.all })
      toast.success(`Started "${task.title}"`, {
        description: "Task marked as In Progress in adaptive schedule.",
      })
    } catch {
      toast.error("Failed to start task. Please try again.")
    } finally {
      setIsStarting(false)
    }
  }

  return (
    <div
      className={cn(
        "relative flex flex-col justify-between overflow-hidden rounded-lg border border-border bg-card p-5 sm:p-6 shadow-2xs transition-colors hover:border-neutral-300 dark:hover:border-neutral-700",
        className
      )}
    >
      {/* Top Tag & Badges */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className="border-orange-500/40 bg-orange-500/10 text-orange-600 dark:text-orange-400 font-semibold tracking-wider text-[10px] uppercase"
          >
            RECOMMENDED NEXT
          </Badge>
          {urgencyLabel && (
            <span className="text-xs font-medium text-muted-foreground">
              {urgencyLabel}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <PriorityBadge priority={task.priority} />
          <StatusBadge status={task.status} />
        </div>
      </div>

      {/* Task Title & Details */}
      <div className="mt-4 flex flex-col gap-2">
        <Link
          href={`/tasks/${task.id}`}
          className="group text-lg sm:text-xl font-semibold tracking-tight text-foreground hover:text-primary transition-colors"
        >
          {task.title}
        </Link>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-muted-foreground">
          <span className="font-medium text-foreground/80">{task.category}</span>
          <span>•</span>
          <DeadlineIndicator deadline={task.deadline} isCompleted={isCompleted} />
          <span>•</span>
          <span className="inline-flex items-center gap-1 font-medium text-foreground">
            <Clock className="size-3.5 text-muted-foreground" />
            <span className="tabular-nums">{task.remainingDuration}h</span> remaining
          </span>
        </div>
      </div>

      {/* Recommendation Explanation Box */}
      <div className="mt-4 flex items-start gap-2.5 rounded-md border border-neutral-200 bg-neutral-50/80 p-3 text-xs leading-relaxed text-muted-foreground dark:border-neutral-800 dark:bg-neutral-900/50">
        <Sparkles className="size-4 shrink-0 text-orange-500 mt-0.5" />
        <div className="flex flex-col gap-0.5">
          <span className="font-medium text-foreground text-[11px] uppercase tracking-wider">
            Adaptive Reason
          </span>
          <p className="text-xs text-neutral-600 dark:text-neutral-400">
            {recommendationReason}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-5 flex flex-wrap items-center gap-2.5 pt-1">
        {!isCompleted && (
          <Button
            variant={isInProgress ? "secondary" : "primary"}
            size="sm"
            onClick={handleStartTask}
            disabled={isInProgress || isStarting}
            className="gap-1.5"
          >
            <Play className="size-3.5 fill-current" />
            <span>
              {isStarting
                ? "Starting..."
                : isInProgress
                ? "Currently In Progress"
                : "Start Task"}
            </span>
          </Button>
        )}
        <Link href={`/tasks/${task.id}`}>
          <Button variant="outline" size="sm" className="gap-1.5">
            <span>View Task Details</span>
            <ArrowRight className="size-3.5" />
          </Button>
        </Link>
      </div>
    </div>
  )
}
