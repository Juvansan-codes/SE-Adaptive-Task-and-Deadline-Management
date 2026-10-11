"use client"

import * as React from "react"
import {
  Search,
  Plus,
  LayoutGrid,
  List as ListIcon,
  X,
  Trash2,
  Loader2,
} from "lucide-react"
import { toast } from "sonner"

import type { Task, TaskFilterOptions, TaskStatus, TaskPriority } from "@/types/task"
import {
  useTasks,
  useCategories,
  useDeleteTask,
  useUpdateTaskStatus,
} from "@/hooks/use-tasks"
import { TaskCard } from "./task-card"
import { TaskRow } from "./task-row"
import { TaskForm } from "./task-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import { EmptyState } from "@/components/common/empty-state"
import { LoadingState } from "@/components/common/loading-state"
import { ErrorState } from "@/components/common/error-state"

export function TaskList() {
  // Filter and view state
  const [search, setSearch] = React.useState("")
  const [status, setStatus] = React.useState<TaskStatus | "all">("all")
  const [priority, setPriority] = React.useState<TaskPriority | "all">("all")
  const [category, setCategory] = React.useState<string>("all")
  const [sortBy, setSortBy] = React.useState<NonNullable<TaskFilterOptions["sortBy"]>>("deadline")
  const [viewMode, setViewMode] = React.useState<"grid" | "list">("grid")

  // Modal dialog states
  const [formOpen, setFormOpen] = React.useState(false)
  const [editingTask, setEditingTask] = React.useState<Task | null>(null)
  const [deletingTask, setDeletingTask] = React.useState<Task | null>(null)

  // Service queries & mutations
  const filterOptions: TaskFilterOptions = React.useMemo(
    () => ({
      search: search.trim(),
      status: status === "all" ? undefined : status,
      priority: priority === "all" ? undefined : priority,
      category: category === "all" ? undefined : category,
      sortBy,
      sortDirection: "asc",
    }),
    [search, status, priority, category, sortBy]
  )

  const { data: tasks, isLoading, isError, error, refetch } = useTasks(filterOptions)
  const { data: categories = [] } = useCategories()
  const deleteTask = useDeleteTask()
  const updateStatus = useUpdateTaskStatus()

  // Clear filters
  const hasActiveFilters = search !== "" || status !== "all" || priority !== "all" || category !== "all"

  const handleClearFilters = () => {
    setSearch("")
    setStatus("all")
    setPriority("all")
    setCategory("all")
    setSortBy("deadline")
  }

  // Quick status toggle
  const handleStatusChange = async (task: Task, newStatus: TaskStatus) => {
    try {
      await updateStatus.mutateAsync({ id: task.id, status: newStatus })
      toast.success(
        newStatus === "completed"
          ? "Task marked as completed."
          : `Task status updated to ${newStatus}.`
      )
    } catch {
      toast.error("Failed to update status.")
    }
  }

  // Handle delete execution
  const handleConfirmDelete = async () => {
    if (!deletingTask) return
    try {
      await deleteTask.mutateAsync(deletingTask.id)
      toast.success("Task deleted successfully.")
      setDeletingTask(null)
    } catch {
      toast.error("Failed to delete task.")
    }
  }

  const openCreateDialog = () => {
    setEditingTask(null)
    setFormOpen(true)
  }

  const openEditDialog = (task: Task) => {
    setEditingTask(task)
    setFormOpen(true)
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Top Header & Quick Actions */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground md:text-2xl">
            Tasks
          </h1>
          <p className="text-xs text-muted-foreground sm:text-sm">
            Manage objectives, adjust deadlines, and monitor workload distribution.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* View toggle */}
          <div className="flex items-center rounded-md border border-border bg-background p-0.5">
            <Button
              variant={viewMode === "grid" ? "secondary" : "ghost"}
              size="icon-sm"
              className="size-7"
              onClick={() => setViewMode("grid")}
              aria-label="Grid view"
            >
              <LayoutGrid className="size-3.5" />
            </Button>
            <Button
              variant={viewMode === "list" ? "secondary" : "ghost"}
              size="icon-sm"
              className="size-7"
              onClick={() => setViewMode("list")}
              aria-label="List view"
            >
              <ListIcon className="size-3.5" />
            </Button>
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={openCreateDialog}
          >
            <Plus className="size-3.5" />
            <span>Create Task</span>
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col gap-2.5 rounded-lg border border-border bg-card p-3 shadow-2xs">
        <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-5">
          {/* Search Input */}
          <div className="relative sm:col-span-2 lg:col-span-2">
            <Search className="absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground pointer-events-none" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search tasks, categories..."
              className="pl-8.5 pr-8 h-9"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch("")}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                aria-label="Clear search"
              >
                <X className="size-3.5" />
              </button>
            )}
          </div>

          {/* Status Filter */}
          <div>
            <Select value={status} onValueChange={(val) => setStatus(val as TaskStatus | "all")}>
              <SelectTrigger className="w-full h-9">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="overdue">Overdue</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Priority Filter */}
          <div>
            <Select value={priority} onValueChange={(val) => setPriority(val as TaskPriority | "all")}>
              <SelectTrigger className="w-full h-9">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priorities</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Sort By Filter */}
          <div>
            <Select value={sortBy} onValueChange={(val) => setSortBy(val as NonNullable<TaskFilterOptions["sortBy"]>)}>
              <SelectTrigger className="w-full h-9">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="deadline">Sort: Deadline</SelectItem>
                <SelectItem value="priority">Sort: Priority</SelectItem>
                <SelectItem value="title">Sort: Title</SelectItem>
                <SelectItem value="status">Sort: Status</SelectItem>
                <SelectItem value="progress">Sort: Progress</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Category filters & Active reset pill */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border/60 text-xs">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-muted-foreground font-medium mr-1 text-[11px]">Category:</span>
            <button
              type="button"
              onClick={() => setCategory("all")}
              className={`rounded px-2 py-0.5 text-xs font-medium transition-colors cursor-pointer ${
                category === "all"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-muted-foreground hover:text-foreground"
              }`}
            >
              All
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setCategory(cat)}
                className={`rounded px-2 py-0.5 text-xs font-medium transition-colors cursor-pointer ${
                  category === cat
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-muted-foreground hover:text-foreground"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearFilters}
              className="h-6 text-xs text-muted-foreground hover:text-foreground"
            >
              <X className="size-3" />
              <span>Clear filters</span>
            </Button>
          )}
        </div>
      </div>

      {/* Task List Rendering */}
      {isLoading ? (
        <LoadingState message="Loading tasks from workspace..." />
      ) : isError ? (
        <ErrorState
          title="Failed to load tasks"
          message={error instanceof Error ? error.message : "An unexpected error occurred."}
          onRetry={() => refetch()}
        />
      ) : tasks && tasks.length > 0 ? (
        viewMode === "grid" ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onEdit={openEditDialog}
                onDelete={setDeletingTask}
                onStatusChange={handleStatusChange}
              />
            ))}
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {tasks.map((task) => (
              <TaskRow
                key={task.id}
                task={task}
                onEdit={openEditDialog}
                onDelete={setDeletingTask}
                onStatusChange={handleStatusChange}
              />
            ))}
          </div>
        )
      ) : (
        <div className="rounded-lg border border-border bg-card p-8">
          <EmptyState
            title={hasActiveFilters ? "No matching tasks found" : "No tasks in workspace"}
            description={
              hasActiveFilters
                ? "Try broadening your search term or resetting active filters."
                : "Create your first task to begin tracking deadlines and workload distribution."
            }
            action={
              hasActiveFilters ? (
                <Button variant="outline" size="sm" onClick={handleClearFilters}>
                  Clear all filters
                </Button>
              ) : (
                <Button variant="primary" size="sm" onClick={openCreateDialog}>
                  <Plus className="size-3.5" />
                  <span>Create First Task</span>
                </Button>
              )
            }
          />
        </div>
      )}

      {/* Task Create / Edit Dialog */}
      <TaskForm
        open={formOpen}
        onOpenChange={setFormOpen}
        task={editingTask}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={!!deletingTask}
        onOpenChange={(open) => !open && setDeletingTask(null)}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Delete Task</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete{" "}
              <strong className="text-foreground font-semibold">
                &ldquo;{deletingTask?.title}&rdquo;
              </strong>
              ? This action will remove the task from the in-memory schedule.
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
                <>
                  <Trash2 className="size-3.5" />
                  <span>Delete Task</span>
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
