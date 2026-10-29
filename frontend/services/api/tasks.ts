/**
 * Real Task Service connected to FastAPI /api/tasks endpoints.
 */

import { apiClient } from "./client"
import type {
  Task,
  TaskFilterOptions,
  CreateTaskInput,
  UpdateTaskInput,
} from "@/types/task"

export const taskService = {
  /**
   * Retrieve filtered and sorted tasks.
   */
  async getTasks(filter?: TaskFilterOptions): Promise<Task[]> {
    const params: Record<string, string | undefined> = {}

    if (filter) {
      if (filter.search && filter.search.trim()) {
        params.search = filter.search.trim()
      }
      if (filter.status && filter.status !== "all") {
        params.status = filter.status
      }
      if (filter.priority && filter.priority !== "all") {
        params.priority = filter.priority
      }
      if (filter.category && filter.category !== "all") {
        params.category = filter.category
      }
      if (filter.sortBy) {
        params.sort_by = filter.sortBy
      }
      if (filter.sortDirection) {
        params.sort_order = filter.sortDirection
      }
    }

    return apiClient.get<Task[]>("/tasks", { params })
  },

  /**
   * Retrieve a single task by ID.
   */
  async getTask(id: string): Promise<Task | null> {
    try {
      return await apiClient.get<Task>(`/tasks/${id}`)
    } catch (err: unknown) {
      // If 404, return null cleanly
      if (err && typeof err === "object" && "status" in err && err.status === 404) {
        return null
      }
      throw err
    }
  },

  /**
   * Create a new task.
   */
  async createTask(input: CreateTaskInput): Promise<Task> {
    return apiClient.post<Task>("/tasks", input)
  },

  /**
   * Update an existing task.
   */
  async updateTask(id: string, updates: UpdateTaskInput): Promise<Task> {
    return apiClient.patch<Task>(`/tasks/${id}`, updates)
  },

  /**
   * Delete a task by ID.
   */
  async deleteTask(id: string): Promise<boolean> {
    await apiClient.delete(`/tasks/${id}`)
    return true
  },

  /**
   * Retrieve list of unique task categories.
   */
  async getCategories(): Promise<string[]> {
    return apiClient.get<string[]>("/tasks/categories")
  },

  /**
   * Seed sample academic microproject tasks.
   */
  async seedStarterTasks(): Promise<Task[]> {
    return apiClient.post<Task[]>("/tasks/seed")
  },
}
