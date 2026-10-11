"use client"

import * as React from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { format, parseISO, isValid } from "date-fns"
import {
  ArrowLeft,
  Pencil,
  Trash2,
  CheckCircle2,
  Clock,
  Calendar,
  Layers,
  Sparkles,
  Loader2,
} from "lucide-react"
import { toast } from "sonner"

import { useTask, useDeleteTask, useUpdateTaskStatus } from "@/hooks/use-tasks"
import type { TaskStatus } from "@/types/task"
import { PriorityBadge } from "./priority-badge"
import { StatusBadge } from "./status-badge"
import { DifficultyBadge } from "./difficulty-badge"
import { ProgressBar } from "./progress-bar"
import { DeadlineIndicator } from "./deadline-indicator"
import { TaskForm } from "./task-form"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { LoadingState } from "@/components/common/loading-state"
import { ErrorState } from "@/components/common/error-state"

interface TaskDetailsProps {
  taskId: string
}

export function TaskDetails({ taskId }: TaskDetailsProps) {
  const router = useRouter()
  const { data: task, isLoading, isError, error, refetch } = useTask(taskId)
  const deleteTask = useDeleteTask()
  const updateStatus = useUpdateTaskStatus()

  const [editOpen, setEditOpen] = React.useState(false)
  const [deleteOpen, setDeleteOpen] = React.useState(false)

  // Status update handler
  const handleStatusChange = async (newStatus: TaskStatus) => {
    if (!task) return
    try {
      await updateStatus.mutateAsync({ id: task.id, status: newStatus })
      toast.success(`Task status changed to ${newStatus}.`)
    } catch {
      toast.error("Failed to update status.")
    }
  }

  // Delete handler
  const handleConfirmDelete = async () => {
    if (!task) return
    try {
      await deleteTask.mutateAsync(task.id)
      toast.success("Task deleted successfully.")
      router.push("/tasks")
    } catch {
      toast.error("Failed to delete task.")
    }
  }

  if (isLoading) {
    return <LoadingState message="Loading task details..." />
  }

  if (isError) {
    return (
      <ErrorState
        title="Error loading task"
        message={error instanceof Error ? error.message : "An unexpected error occurred."}
        onRetry={() => refetch()}
        action={
          <Link href="/tasks">
            <Button variant="outline" size="sm">
              <ArrowLeft className="size-3.5" />
              <span>Back to Tasks</span>
            </Button>
          </Link>
        }
      />
    )
  }

  if (!task) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center rounded-lg border border-border bg-card">
        <h2 className="text-lg font-semibold text-foreground">Task Not Found</h2>
        <p className="mt-1 text-xs text-muted-foreground max-w-sm">
          The requested task ID &ldquo;{taskId}&rdquo; does not exist or was removed from this workspace.
        </p>
        <Link href="/tasks" className="mt-4">
          <Button variant="primary" size="sm">
            <ArrowLeft className="size-3.5" />
            <span>Return to Task List</span>
          </Button>
        </Link>
      </div>
    )
  }

  const isCompleted = task.status === "completed"

  const formatDateString = (isoString?: string) => {
    if (!isoString) return "N/A"
    try {
      const parsed = parseISO(isoString)
      return isValid(parsed) ? format(parsed, "MMM d, yyyy 'at' h:mm a") : isoString
    } catch {
      return isoString
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Top Navigation & Action Bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Link
          href="/tasks"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors w-fit"
        >
          <ArrowLeft className="size-3.5" />
          <span>Back to Tasks</span>
        </Link>

        <div className="flex items-center gap-2">
          {/* Status Quick Toggle */}
          <DropdownMenu>
            <DropdownMenuTrigger render={<Button variant="outline" size="sm" className="gap-1.5" />}>
              <StatusBadge status={task.status} />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleStatusChange("pending")}>
                Set Pending
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleStatusChange("in_progress")}>
                Set In Progress
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleStatusChange("completed")}>
                <CheckCircle2 className="size-3.5 text-emerald-600" />
                <span>Set Completed</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleStatusChange("overdue")}>
                Set Overdue
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setEditOpen(true)}
          >
            <Pencil className="size-3.5" />
            <span>Edit</span>
          </Button>

          <Button
            variant="destructive"
            size="sm"
            onClick={() => setDeleteOpen(true)}
          >
            <Trash2 className="size-3.5" />
            <span>Delete</span>
          </Button>
        </div>
      </div>

      {/* Main Grid: Details Overview + Metrics Sidebar */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Column (2 Cols): Task Content & Description */}
        <div className="flex flex-col gap-6 lg:col-span-2">
          {/* Main Info Card */}
          <div className="flex flex-col gap-4 rounded-lg border border-border bg-card p-6 shadow-2xs">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded bg-secondary px-2.5 py-0.5 text-xs font-medium text-muted-foreground border border-border/50">
                {task.category}
              </span>
              <PriorityBadge priority={task.priority} />
              <DifficultyBadge difficulty={task.difficulty} />
              <StatusBadge status={task.status} />
            </div>

            <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
              {task.title}
            </h1>

            <div className="space-y-2 border-t border-border/70 pt-4">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Description &amp; Objectives
              </h2>
              {task.description ? (
                <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap">
                  {task.description}
                </p>
              ) : (
                <p className="text-xs italic text-muted-foreground">
                  No additional description provided for this task.
                </p>
              )}
            </div>
          </div>

          {/* Progress Card */}
          <div className="flex flex-col gap-4 rounded-lg border border-border bg-card p-6 shadow-2xs">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold tracking-tight text-foreground">
                Progress &amp; Completion
              </h2>
              <span className="text-sm font-bold tabular-nums text-foreground">
                {task.progress}%
              </span>
            </div>

            <ProgressBar
              progress={task.progress}
              completedDuration={task.completedDuration}
              estimatedDuration={task.estimatedDuration}
              showLabel={false}
              size="default"
            />

            <div className="grid grid-cols-3 gap-3 pt-2 text-center">
              <div className="rounded-md border border-border/60 bg-secondary/30 p-2.5">
                <span className="text-[11px] text-muted-foreground block">Estimated</span>
                <span className="text-sm font-semibold text-foreground tabular-nums">
                  {task.estimatedDuration}h
                </span>
              </div>
              <div className="rounded-md border border-border/60 bg-secondary/30 p-2.5">
                <span className="text-[11px] text-muted-foreground block">Completed</span>
                <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400 tabular-nums">
                  {task.completedDuration}h
                </span>
              </div>
              <div className="rounded-md border border-border/60 bg-secondary/30 p-2.5">
                <span className="text-[11px] text-muted-foreground block">Remaining</span>
                <span className="text-sm font-semibold text-primary tabular-nums">
                  {task.remainingDuration}h
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Parameters & Timestamps */}
        <div className="flex flex-col gap-6">
          {/* Metadata Parameters Card */}
          <div className="flex flex-col gap-4 rounded-lg border border-border bg-card p-5 shadow-2xs">
            <h2 className="text-sm font-semibold tracking-tight text-foreground">
              Schedule Parameters
            </h2>

            <div className="space-y-3.5 text-xs">
              <div className="flex items-center justify-between border-b border-border/60 pb-2">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Calendar className="size-3.5" />
                  <span>Target Deadline</span>
                </span>
                <DeadlineIndicator deadline={task.deadline} isCompleted={isCompleted} />
              </div>

              <div className="flex items-center justify-between border-b border-border/60 pb-2">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Sparkles className="size-3.5" />
                  <span>Priority Tier</span>
                </span>
                <PriorityBadge priority={task.priority} />
              </div>

              <div className="flex items-center justify-between border-b border-border/60 pb-2">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Layers className="size-3.5" />
                  <span>Complexity</span>
                </span>
                <DifficultyBadge difficulty={task.difficulty} />
              </div>

              <div className="flex items-center justify-between border-b border-border/60 pb-2">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Clock className="size-3.5" />
                  <span>Category</span>
                </span>
                <span className="font-medium text-foreground">{task.category}</span>
              </div>
            </div>
          </div>

          {/* Audit Timestamps Card */}
          <div className="flex flex-col gap-3 rounded-lg border border-border bg-card p-5 text-xs text-muted-foreground shadow-2xs">
            <h3 className="font-semibold text-foreground text-xs uppercase tracking-wider">
              Audit Trail
            </h3>
            <div className="space-y-1.5">
              <div className="flex justify-between">
                <span>Created:</span>
                <span className="font-medium text-foreground">{formatDateString(task.createdAt)}</span>
              </div>
              <div className="flex justify-between">
                <span>Last Updated:</span>
                <span className="font-medium text-foreground">{formatDateString(task.updatedAt)}</span>
              </div>
              <div className="flex justify-between">
                <span>Internal ID:</span>
                <span className="font-mono text-[11px]">{task.id}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Dialog */}
      <TaskForm
        open={editOpen}
        onOpenChange={setEditOpen}
        task={task}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Delete Task</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &ldquo;{task.title}&rdquo;? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="pt-2">
            <DialogClose render={<Button variant="outline" size="sm" disabled={deleteTask.isPending} />}>
              Cancel
            </DialogClose>
            <Button
              variant="destructive"
              size="sm"
              onClick={handleConfirmDelete}
              disabled={deleteTask.isPending}
            >
              {deleteTask.isPending ? (
                <>
                  <Loader2 className="size-3.5 animate-spin motion-reduce:animate-none" />
                  <span>Deleting...</span>
                </>
              ) : (
                <span>Confirm Delete</span>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
