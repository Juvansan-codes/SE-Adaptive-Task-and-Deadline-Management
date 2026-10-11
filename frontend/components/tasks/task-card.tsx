"use client"

import * as React from "react"
import Link from "next/link"
import { MoreHorizontal, ArrowRight, Pencil, Trash2, CheckCircle2 } from "lucide-react"

import type { Task } from "@/types/task"
import { PriorityBadge } from "./priority-badge"
import { StatusBadge } from "./status-badge"
import { DifficultyBadge } from "./difficulty-badge"
import { ProgressBar } from "./progress-bar"
import { DeadlineIndicator } from "./deadline-indicator"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

interface TaskCardProps {
  task: Task
  onEdit?: (task: Task) => void
  onDelete?: (task: Task) => void
  onStatusChange?: (task: Task, status: Task["status"]) => void
  className?: string
}

export function TaskCard({
  task,
  onEdit,
  onDelete,
  onStatusChange,
  className,
}: TaskCardProps) {
  const isCompleted = task.status === "completed"

  return (
    <div
      className={cn(
        "group flex flex-col justify-between rounded-lg border border-border bg-card p-4 transition-all hover:border-neutral-400/60 dark:hover:border-neutral-700 shadow-2xs",
        isCompleted && "bg-neutral-50/50 dark:bg-neutral-900/40 opacity-90",
        className
      )}
    >
      <div className="flex flex-col gap-2.5">
        {/* Top Badges & Actions */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="rounded bg-secondary px-2 py-0.5 text-[11px] font-medium text-muted-foreground border border-border/50">
              {task.category}
            </span>
            <PriorityBadge priority={task.priority} />
            <StatusBadge status={task.status} />
          </div>

          {/* Context Actions */}
          <DropdownMenu>
            <DropdownMenuTrigger render={<Button variant="ghost" size="icon-sm" className="size-7 text-muted-foreground" aria-label="Task options" />}>
              <MoreHorizontal className="size-4" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-44">
              <DropdownMenuItem render={<Link href={`/tasks/${task.id}`} className="flex items-center gap-2 w-full" />}>
                <ArrowRight className="size-3.5" />
                <span>View Details</span>
              </DropdownMenuItem>
              {onEdit && (
                <DropdownMenuItem onClick={() => onEdit(task)}>
                  <Pencil className="size-3.5" />
                  <span>Edit Task</span>
                </DropdownMenuItem>
              )}
              {onStatusChange && !isCompleted && (
                <DropdownMenuItem
                  onClick={() => onStatusChange(task, "completed")}
                >
                  <CheckCircle2 className="size-3.5 text-emerald-600" />
                  <span>Mark Completed</span>
                </DropdownMenuItem>
              )}
              {onStatusChange && isCompleted && (
                <DropdownMenuItem
                  onClick={() => onStatusChange(task, "in_progress")}
                >
                  <CheckCircle2 className="size-3.5" />
                  <span>Re-open Task</span>
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              {onDelete && (
                <DropdownMenuItem
                  onClick={() => onDelete(task)}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="size-3.5" />
                  <span>Delete Task</span>
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Title */}
        <Link
          href={`/tasks/${task.id}`}
          className="group/link block text-sm font-semibold tracking-tight text-foreground hover:text-primary transition-colors line-clamp-2"
        >
          {task.title}
        </Link>

        {/* Description snippet */}
        {task.description && (
          <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
            {task.description}
          </p>
        )}
      </div>

      {/* Bottom Section: Progress & Deadline */}
      <div className="mt-4 pt-3 border-t border-border/70 flex flex-col gap-2.5">
        <ProgressBar
          progress={task.progress}
          completedDuration={task.completedDuration}
          estimatedDuration={task.estimatedDuration}
          size="sm"
        />

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <DeadlineIndicator
            deadline={task.deadline}
            isCompleted={isCompleted}
          />
          <DifficultyBadge difficulty={task.difficulty} />
        </div>
      </div>
    </div>
  )
}
