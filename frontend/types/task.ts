/**
 * Task domain types and interfaces
 * Aligned with the Adaptive Task & Deadline Management specifications.
 */

export type TaskPriority = "low" | "medium" | "high" | "critical"
export type TaskDifficulty = "easy" | "medium" | "hard"
export type TaskStatus = "pending" | "in_progress" | "completed" | "overdue"

export interface Task {
  id: string
  title: string
  description: string
  category: string
  deadline: string // ISO date string or YYYY-MM-DD
  priority: TaskPriority
  difficulty: TaskDifficulty
  estimatedDuration: number // Duration in hours
  completedDuration: number // Duration in hours
  remainingDuration: number // Duration in hours
  progress: number // Percentage 0 - 100
  status: TaskStatus
  createdAt: string
  updatedAt: string
}

export interface TaskFilterOptions {
  search?: string
  status?: TaskStatus | "all"
  priority?: TaskPriority | "all"
  category?: string | "all"
  sortBy?: "deadline" | "priority" | "title" | "status" | "progress"
  sortDirection?: "asc" | "desc"
}

export type CreateTaskInput = {
  title: string
  description?: string
  category: string
  deadline: string
  priority: TaskPriority
  difficulty: TaskDifficulty
  estimatedDuration: number
  completedDuration?: number
  status?: TaskStatus
}

export type UpdateTaskInput = Partial<CreateTaskInput> & {
  completedDuration?: number
  status?: TaskStatus
}
