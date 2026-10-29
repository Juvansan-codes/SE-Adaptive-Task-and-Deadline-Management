"use client"

import * as React from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

import { taskFormSchema, type TaskFormData } from "@/lib/validations/task"
import { useCreateTask, useUpdateTask, useCategories } from "@/hooks/use-tasks"
import type { Task } from "@/types/task"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface TaskFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  task?: Task | null
  onSuccess?: (task: Task) => void
}

export function TaskForm({
  open,
  onOpenChange,
  task,
  onSuccess,
}: TaskFormProps) {
  const isEditing = !!task
  const createTask = useCreateTask()
  const updateTask = useUpdateTask()
  const { data: existingCategories = [] } = useCategories()

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskFormSchema),
    defaultValues: {
      title: "",
      description: "",
      category: "Engineering",
      deadline: "",
      priority: "medium",
      difficulty: "medium",
      estimatedDuration: 4,
      completedDuration: 0,
      status: "pending",
    },
  })

  // Synchronize form values when task changes or dialog opens
  React.useEffect(() => {
    if (open) {
      const getInitialDate = () => {
        if (task?.deadline) {
          return task.deadline.slice(0, 10)
        }
        const future = new Date()
        future.setDate(future.getDate() + 5)
        return future.toISOString().slice(0, 10)
      }
      const initialDate = getInitialDate()

      if (task) {
        reset({
          title: task.title,
          description: task.description || "",
          category: task.category,
          deadline: initialDate,
          priority: task.priority,
          difficulty: task.difficulty,
          estimatedDuration: task.estimatedDuration,
          completedDuration: task.completedDuration,
          status: task.status,
        })
      } else {
        reset({
          title: "",
          description: "",
          category: existingCategories[0] || "Engineering",
          deadline: initialDate,
          priority: "medium",
          difficulty: "medium",
          estimatedDuration: 4,
          completedDuration: 0,
          status: "pending",
        })
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, task, reset])

  const onSubmit = async (formData: TaskFormData) => {
    try {
      const formattedDeadline = `${formData.deadline}T18:00:00Z`

      if (isEditing && task) {
        const updated = await updateTask.mutateAsync({
          id: task.id,
          updates: {
            ...formData,
            deadline: formattedDeadline,
          },
        })
        if (updated) {
          toast.success("Task updated successfully.")
          onSuccess?.(updated)
        }
      } else {
        const created = await createTask.mutateAsync({
          ...formData,
          deadline: formattedDeadline,
        })
        toast.success("Task created successfully.")
        onSuccess?.(created)
      }

      onOpenChange(false)
    } catch {
      toast.error(isEditing ? "Failed to update task." : "Failed to create task.")
    }
  }

  const isLoading = isSubmitting || createTask.isPending || updateTask.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? "Edit Task Details" : "Create New Task"}
          </DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Update task parameters, estimated durations, and priority levels."
              : "Define a task objective, deadline, duration estimates, and initial status."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-2" noValidate>
          {/* Title */}
          <div className="space-y-1.5">
            <label htmlFor="task-title" className="text-xs font-medium text-foreground">
              Task Title <span className="text-destructive">*</span>
            </label>
            <Input
              id="task-title"
              placeholder="e.g. Implement OAuth Flow"
              disabled={isLoading}
              aria-invalid={!!errors.title}
              {...register("title")}
            />
            {errors.title && (
              <p className="text-xs text-destructive">{errors.title.message}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-1.5">
            <label htmlFor="task-desc" className="text-xs font-medium text-foreground">
              Description
            </label>
            <textarea
              id="task-desc"
              rows={3}
              placeholder="Detailed description of deliverables, constraints, or notes..."
              disabled={isLoading}
              className="w-full rounded-md border border-input bg-background p-2.5 text-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40 disabled:cursor-not-allowed disabled:opacity-50"
              {...register("description")}
            />
            {errors.description && (
              <p className="text-xs text-destructive">{errors.description.message}</p>
            )}
          </div>

          {/* Row: Category & Deadline */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label htmlFor="task-category" className="text-xs font-medium text-foreground">
                Category <span className="text-destructive">*</span>
              </label>
              <Input
                id="task-category"
                placeholder="e.g. Engineering"
                disabled={isLoading}
                aria-invalid={!!errors.category}
                {...register("category")}
              />
              {errors.category && (
                <p className="text-xs text-destructive">{errors.category.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label htmlFor="task-deadline" className="text-xs font-medium text-foreground">
                Target Deadline <span className="text-destructive">*</span>
              </label>
              <Input
                id="task-deadline"
                type="date"
                disabled={isLoading}
                aria-invalid={!!errors.deadline}
                {...register("deadline")}
              />
              {errors.deadline && (
                <p className="text-xs text-destructive">{errors.deadline.message}</p>
              )}
            </div>
          </div>

          {/* Row: Priority & Difficulty */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-foreground">
                Priority <span className="text-destructive">*</span>
              </label>
              <Controller
                name="priority"
                control={control}
                render={({ field }) => (
                  <Select
                    value={field.value}
                    onValueChange={field.onChange}
                    disabled={isLoading}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low Priority</SelectItem>
                      <SelectItem value="medium">Medium Priority</SelectItem>
                      <SelectItem value="high">High Priority</SelectItem>
                      <SelectItem value="critical">Critical Priority</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
              {errors.priority && (
                <p className="text-xs text-destructive">{errors.priority.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-foreground">
                Difficulty <span className="text-destructive">*</span>
              </label>
              <Controller
                name="difficulty"
                control={control}
                render={({ field }) => (
                  <Select
                    value={field.value}
                    onValueChange={field.onChange}
                    disabled={isLoading}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select difficulty" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="easy">Easy (Low Complexity)</SelectItem>
                      <SelectItem value="medium">Medium (Moderate Complexity)</SelectItem>
                      <SelectItem value="hard">Hard (High Complexity)</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
              {errors.difficulty && (
                <p className="text-xs text-destructive">{errors.difficulty.message}</p>
              )}
            </div>
          </div>

          {/* Row: Estimated & Completed Duration */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label htmlFor="task-est" className="text-xs font-medium text-foreground">
                Estimated Hours <span className="text-destructive">*</span>
              </label>
              <Input
                id="task-est"
                type="number"
                step="0.5"
                min="0.5"
                placeholder="4"
                disabled={isLoading}
                aria-invalid={!!errors.estimatedDuration}
                {...register("estimatedDuration")}
              />
              {errors.estimatedDuration && (
                <p className="text-xs text-destructive">
                  {errors.estimatedDuration.message}
                </p>
              )}
            </div>

            <div className="space-y-1.5">
              <label htmlFor="task-completed" className="text-xs font-medium text-foreground">
                Completed Hours
              </label>
              <Input
                id="task-completed"
                type="number"
                step="0.5"
                min="0"
                placeholder="0"
                disabled={isLoading}
                aria-invalid={!!errors.completedDuration}
                {...register("completedDuration")}
              />
              {errors.completedDuration && (
                <p className="text-xs text-destructive">
                  {errors.completedDuration.message}
                </p>
              )}
            </div>
          </div>

          {/* Status field */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-foreground">
              Current Status
            </label>
            <Controller
              name="status"
              control={control}
              render={({ field }) => (
                <Select
                  value={field.value}
                  onValueChange={field.onChange}
                  disabled={isLoading}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="overdue">Overdue</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
          </div>

          <DialogFooter className="pt-3">
            <DialogClose render={<Button variant="outline" size="sm" disabled={isLoading} />}>
              Cancel
            </DialogClose>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="size-3.5 animate-spin motion-reduce:animate-none" />
                  <span>Saving...</span>
                </>
              ) : (
                <span>{isEditing ? "Save Changes" : "Create Task"}</span>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
