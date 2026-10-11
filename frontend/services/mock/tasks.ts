/**
 * ==============================================================================
 * MOCK TASK MANAGEMENT SERVICE
 * ==============================================================================
 * DISCLAIMER:
 * This service manages in-memory mock task entities for Phase 3 UI functionality.
 * - Simulates asynchronous API requests with artificial network latency.
 * - Persists state in-memory across client-side navigation within the active session.
 * - Designed with a clean interface that can be replaced with FastAPI endpoints.
 * ==============================================================================
 */

import type {
  Task,
  TaskFilterOptions,
  CreateTaskInput,
  UpdateTaskInput,
} from "@/types/task"

const simulateLatency = (ms: number = 300): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms))

// Helper to compute progress and remaining duration
function calculateDerivedFields(estimated: number, completed: number) {
  const safeEstimated = Math.max(0.1, estimated)
  const safeCompleted = Math.max(0, completed)
  const remaining = Math.max(0, Number((safeEstimated - safeCompleted).toFixed(1)))
  const progress = Math.min(100, Math.max(0, Math.round((safeCompleted / safeEstimated) * 100)))
  return { remainingDuration: remaining, progress }
}

// Initial seed tasks representing a realistic productivity workload
const INITIAL_TASKS: Task[] = [
  {
    id: "task-101",
    title: "Implement Core Data Ingestion Pipeline",
    description: "Build robust streaming connectors to ingest task metadata and deadline timestamps from upstream sources.",
    category: "Engineering",
    deadline: "2026-10-18T18:00:00Z",
    priority: "critical",
    difficulty: "hard",
    estimatedDuration: 16,
    completedDuration: 12,
    remainingDuration: 4,
    progress: 75,
    status: "in_progress",
    createdAt: "2026-10-08T09:00:00Z",
    updatedAt: "2026-10-11T14:30:00Z",
  },
  {
    id: "task-102",
    title: "Design Accessibility Audit for Form Controls",
    description: "Verify all inputs, selects, and dialog triggers adhere to WCAG 2.1 AA standards including keyboard focus and aria-labels.",
    category: "Design",
    deadline: "2026-10-14T17:00:00Z",
    priority: "high",
    difficulty: "medium",
    estimatedDuration: 6,
    completedDuration: 4.5,
    remainingDuration: 1.5,
    progress: 75,
    status: "in_progress",
    createdAt: "2026-10-09T10:15:00Z",
    updatedAt: "2026-10-11T11:00:00Z",
  },
  {
    id: "task-103",
    title: "Refactor Legacy API Response Serializers",
    description: "Consolidate response formats to match unified OpenAPI 3.1 schema specification with strict type validation.",
    category: "Engineering",
    deadline: "2026-10-10T12:00:00Z", // Past date for overdue demonstration
    priority: "high",
    difficulty: "medium",
    estimatedDuration: 8,
    completedDuration: 3,
    remainingDuration: 5,
    progress: 38,
    status: "overdue",
    createdAt: "2026-10-05T08:00:00Z",
    updatedAt: "2026-10-10T12:30:00Z",
  },
  {
    id: "task-104",
    title: "Setup CI/CD Automated Lint & Type-Check Gates",
    description: "Configure GitHub Actions workflows to execute ESLint and TypeScript compiler verification on every pull request.",
    category: "DevOps",
    deadline: "2026-10-12T20:00:00Z",
    priority: "medium",
    difficulty: "easy",
    estimatedDuration: 4,
    completedDuration: 4,
    remainingDuration: 0,
    progress: 100,
    status: "completed",
    createdAt: "2026-10-07T14:00:00Z",
    updatedAt: "2026-10-11T09:45:00Z",
  },
  {
    id: "task-105",
    title: "Draft Adaptive Scheduling Heuristic Specifications",
    description: "Outline requirements for dynamic timeline shifting, constraint satisfaction, and buffer duration allocation.",
    category: "Product",
    deadline: "2026-10-22T18:00:00Z",
    priority: "critical",
    difficulty: "hard",
    estimatedDuration: 20,
    completedDuration: 2,
    remainingDuration: 18,
    progress: 10,
    status: "pending",
    createdAt: "2026-10-10T16:00:00Z",
    updatedAt: "2026-10-10T16:00:00Z",
  },
  {
    id: "task-106",
    title: "End-to-End User Flow Smoke Testing",
    description: "Run automated browser walkthroughs verifying login, dashboard, task list, and detail screen renders.",
    category: "Quality Assurance",
    deadline: "2026-10-19T15:00:00Z",
    priority: "medium",
    difficulty: "medium",
    estimatedDuration: 10,
    completedDuration: 0,
    remainingDuration: 10,
    progress: 0,
    status: "pending",
    createdAt: "2026-10-11T12:00:00Z",
    updatedAt: "2026-10-11T12:00:00Z",
  },
  {
    id: "task-107",
    title: "Write Developer Setup and Onboarding Documentation",
    description: "Create comprehensive instructions for local environment setup, environment variable configuration, and test runs.",
    category: "Documentation",
    deadline: "2026-10-25T17:00:00Z",
    priority: "low",
    difficulty: "easy",
    estimatedDuration: 5,
    completedDuration: 5,
    remainingDuration: 0,
    progress: 100,
    status: "completed",
    createdAt: "2026-10-06T11:00:00Z",
    updatedAt: "2026-10-09T16:00:00Z",
  },
]

// In-memory persistent state during application lifetime
let mockTasksStore: Task[] = [...INITIAL_TASKS]

export const mockTaskService = {
  /**
   * Retrieve all tasks with optional search, filtering, and sorting
   */
  async getTasks(filter?: TaskFilterOptions): Promise<Task[]> {
    await simulateLatency(250)

    let result = [...mockTasksStore]

    if (!filter) {
      return result
    }

    // 1. Text Search (title, description, category)
    if (filter.search && filter.search.trim().length > 0) {
      const q = filter.search.trim().toLowerCase()
      result = result.filter(
        (t) =>
          t.title.toLowerCase().includes(q) ||
          t.description.toLowerCase().includes(q) ||
          t.category.toLowerCase().includes(q)
      )
    }

    // 2. Status Filter
    if (filter.status && filter.status !== "all") {
      result = result.filter((t) => t.status === filter.status)
    }

    // 3. Priority Filter
    if (filter.priority && filter.priority !== "all") {
      result = result.filter((t) => t.priority === filter.priority)
    }

    // 4. Category Filter
    if (filter.category && filter.category !== "all") {
      result = result.filter((t) => t.category.toLowerCase() === filter.category?.toLowerCase())
    }

    // 5. Sorting
    const direction = filter.sortDirection === "desc" ? -1 : 1
    const priorityWeight: Record<string, number> = {
      critical: 4,
      high: 3,
      medium: 2,
      low: 1,
    }

    if (filter.sortBy) {
      result.sort((a, b) => {
        switch (filter.sortBy) {
          case "deadline":
            return (new Date(a.deadline).getTime() - new Date(b.deadline).getTime()) * direction
          case "priority":
            return ((priorityWeight[b.priority] || 0) - (priorityWeight[a.priority] || 0)) * direction
          case "title":
            return a.title.localeCompare(b.title) * direction
          case "status":
            return a.status.localeCompare(b.status) * direction
          case "progress":
            return (a.progress - b.progress) * direction
          default:
            return 0
        }
      })
    } else {
      // Default sort by updatedAt desc
      result.sort(
        (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      )
    }

    return result
  },

  /**
   * Retrieve a single task by ID
   */
  async getTask(id: string): Promise<Task | null> {
    await simulateLatency(200)
    const task = mockTasksStore.find((t) => t.id === id)
    return task ? { ...task } : null
  },

  /**
   * Create a new task and append to in-memory store
   */
  async createTask(input: CreateTaskInput): Promise<Task> {
    await simulateLatency(350)

    const completed = input.completedDuration || 0
    const { remainingDuration, progress } = calculateDerivedFields(
      input.estimatedDuration,
      completed
    )

    let status = input.status || "pending"
    if (progress === 100 && status !== "completed") {
      status = "completed"
    }

    const newTask: Task = {
      id: `task-${Date.now().toString().slice(-4)}`,
      title: input.title.trim(),
      description: input.description?.trim() || "",
      category: input.category.trim(),
      deadline: input.deadline,
      priority: input.priority,
      difficulty: input.difficulty,
      estimatedDuration: Number(input.estimatedDuration),
      completedDuration: Number(completed),
      remainingDuration,
      progress,
      status,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    mockTasksStore.unshift(newTask)
    return { ...newTask }
  },

  /**
   * Update an existing task in the in-memory store
   */
  async updateTask(id: string, updates: UpdateTaskInput): Promise<Task | null> {
    await simulateLatency(300)

    const index = mockTasksStore.findIndex((t) => t.id === id)
    if (index === -1) {
      return null
    }

    const current = mockTasksStore[index]
    const estimated = updates.estimatedDuration !== undefined ? Number(updates.estimatedDuration) : current.estimatedDuration
    const completed = updates.completedDuration !== undefined ? Number(updates.completedDuration) : current.completedDuration
    const { remainingDuration, progress } = calculateDerivedFields(estimated, completed)

    let status = updates.status !== undefined ? updates.status : current.status
    if (progress === 100 && status !== "completed") {
      status = "completed"
    }

    const updatedTask: Task = {
      ...current,
      ...updates,
      title: updates.title !== undefined ? updates.title.trim() : current.title,
      description: updates.description !== undefined ? (updates.description?.trim() || "") : current.description,
      category: updates.category !== undefined ? updates.category.trim() : current.category,
      estimatedDuration: estimated,
      completedDuration: completed,
      remainingDuration,
      progress,
      status,
      updatedAt: new Date().toISOString(),
    }

    mockTasksStore[index] = updatedTask
    return { ...updatedTask }
  },

  /**
   * Delete a task by ID
   */
  async deleteTask(id: string): Promise<boolean> {
    await simulateLatency(250)

    const initialLength = mockTasksStore.length
    mockTasksStore = mockTasksStore.filter((t) => t.id !== id)
    return mockTasksStore.length < initialLength
  },

  /**
   * Retrieve list of unique categories
   */
  async getCategories(): Promise<string[]> {
    await simulateLatency(150)
    const set = new Set(mockTasksStore.map((t) => t.category))
    return Array.from(set).sort()
  },
}
