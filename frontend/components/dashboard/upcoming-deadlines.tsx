"use client"

import * as React from "react"
import Link from "next/link"
import { Calendar, ArrowRight, Clock } from "lucide-react"

import type { Task } from "@/types"
import { PriorityBadge } from "@/components/tasks/priority-badge"
import { DeadlineIndicator } from "@/components/tasks/deadline-indicator"
import { StatusBadge } from "@/components/tasks/status-badge"
import { EmptyState } from "@/components/common/empty-state"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface UpcomingDeadlinesProps {
  tasks?: Task[]
  isLoading?: boolean
  className?: string
}

export function UpcomingDeadlines({
  tasks = [],
  isLoading = false,
  className,
}: UpcomingDeadlinesProps) {
  if (isLoading) {
    return (
      <div
        className={cn(
          "flex flex-col rounded-[10px] border border-border bg-card p-5 shadow-[0_1px_2px_rgba(0,0,0,0.03)] animate-pulse",
          className
        )}
      >
        <div className="flex items-center justify-between pb-3 border-b border-border/70">
          <div className="h-4 w-36 rounded bg-muted/70" />
          <div className="h-4 w-16 rounded bg-muted/50" />
        </div>
        <div className="space-y-3 pt-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center justify-between rounded-[6px] border border-border p-3"
            >
              <div className="space-y-2">
                <div className="h-4 w-48 rounded bg-muted/70" />
                <div className="h-3 w-28 rounded bg-muted/40" />
              </div>
              <div className="h-6 w-20 rounded bg-muted/60" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div
      className={cn(
        "flex flex-col rounded-[10px] border border-border bg-card p-5 shadow-[0_1px_2px_rgba(0,0,0,0.03)]",
        className
      )}
    >
      {/* Header Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-border/70">
        <div>
          <h3 className="text-[15px] font-semibold tracking-[-0.01em] text-foreground">
            Upcoming Deadlines
          </h3>
          <p className="text-xs text-muted-foreground font-normal">
            Imminent target milestones in chronological order
          </p>
        </div>
        <Link href="/tasks">
          <Button variant="ghost" size="sm" className="h-8 px-2.5 gap-1 text-xs">
            <span>View all</span>
            <ArrowRight className="size-3" />
          </Button>
        </Link>
      </div>

      {/* Task List or Empty State */}
      {tasks.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No upcoming deadlines"
          description="All scheduled tasks for the next 7 days have either been completed or none exist."
        />
      ) : (
        <div className="divide-y divide-border/60">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="group flex flex-col gap-2 py-3 first:pt-3 last:pb-1 sm:flex-row sm:items-center sm:justify-between transition-colors hover:bg-neutral-50/50 dark:hover:bg-neutral-900/40 rounded-[6px] px-2 -mx-2"
            >
              {/* Task Details & Title */}
              <div className="flex flex-col min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <Link
                    href={`/tasks/${task.id}`}
                    className="truncate text-sm font-medium text-foreground hover:text-primary transition-colors"
                  >
                    {task.title}
                  </Link>
                </div>
                <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                  <span>{task.category}</span>
                  <span>•</span>
                  <span className="inline-flex items-center gap-1">
                    <Clock className="size-3 text-muted-foreground/70" />
                    <span className="font-mono tabular-nums">{task.remainingDuration}h</span> left
                  </span>
                  <span>•</span>
                  <StatusBadge status={task.status} showIcon={false} />
                </div>
              </div>

              {/* Deadline & Priority */}
              <div className="flex items-center gap-2.5 sm:shrink-0 pt-1 sm:pt-0">
                <PriorityBadge priority={task.priority} />
                <DeadlineIndicator deadline={task.deadline} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
