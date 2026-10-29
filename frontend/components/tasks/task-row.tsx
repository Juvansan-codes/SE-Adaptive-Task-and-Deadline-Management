"use client"

import * as React from "react"
import Link from "next/link"
import { MoreHorizontal, Pencil, Trash2, CheckCircle2 } from "lucide-react"

import type { Task } from "@/types/task"
import { PriorityBadge } from "./priority-badge"
import { StatusBadge } from "./status-badge"
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

interface TaskRowProps {
  task: Task
  onEdit?: (task: Task) => void
  onDelete?: (task: Task) => void
  onStatusChange?: (task: Task, status: Task["status"]) => void
  className?: string
}

export function TaskRow({
  task,
  onEdit,
  onDelete,
  onStatusChange,
  className,
}: TaskRowProps) {
  const isCompleted = task.status === "completed"

  return (
    <div
      className={cn(
        "group flex items-center justify-between gap-3 rounded-[6px] border border-border bg-card px-4 py-2.5 transition-colors hover:bg-neutral-50/60 dark:hover:bg-neutral-900/60 shadow-[0_1px_2px_rgba(0,0,0,0.02)]",
        isCompleted && "opacity-80 bg-neutral-50/30",
        className
      )}
    >
      {/* Left Title & Status */}
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <StatusBadge status={task.status} showIcon={false} />
        <div className="flex flex-col min-w-0 flex-1">
          <Link
            href={`/tasks/${task.id}`}
            className="truncate text-sm font-medium text-foreground hover:text-primary transition-colors"
          >
            {task.title}
          </Link>
          <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-xs text-muted-foreground mt-0.5">
            <span className="font-normal">{task.category}</span>
            <span>•</span>
            <span className="font-mono tabular-nums">
              {task.completedDuration}h of {task.estimatedDuration}h
            </span>
            <span className="sm:hidden">•</span>
            <span className="sm:hidden inline-flex items-center gap-1.5">
              <PriorityBadge priority={task.priority} showIcon={false} />
              <DeadlineIndicator deadline={task.deadline} isCompleted={isCompleted} showRelative={false} />
            </span>
          </div>
        </div>
      </div>

      {/* Center/Right Meta */}
      <div className="hidden sm:flex items-center gap-3 shrink-0">
        <PriorityBadge priority={task.priority} />
        <DeadlineIndicator deadline={task.deadline} isCompleted={isCompleted} showRelative={false} />
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1 shrink-0">
        <DropdownMenu>
          <DropdownMenuTrigger render={<Button variant="ghost" size="icon-sm" className="size-8 rounded-[6px] text-muted-foreground" aria-label="Task options" />}>
            <MoreHorizontal className="size-4" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-40 rounded-[8px]">
            <DropdownMenuItem render={<Link href={`/tasks/${task.id}`} className="w-full" />}>
              View Details
            </DropdownMenuItem>
            {onEdit && (
              <DropdownMenuItem onClick={() => onEdit(task)}>
                <Pencil className="size-3.5" />
                <span>Edit</span>
              </DropdownMenuItem>
            )}
            {onStatusChange && (
              <DropdownMenuItem
                onClick={() =>
                  onStatusChange(task, isCompleted ? "in_progress" : "completed")
                }
              >
                <CheckCircle2 className="size-3.5" />
                <span>{isCompleted ? "Re-open" : "Complete"}</span>
              </DropdownMenuItem>
            )}
            <DropdownMenuSeparator />
            {onDelete && (
              <DropdownMenuItem
                onClick={() => onDelete(task)}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="size-3.5" />
                <span>Delete</span>
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
