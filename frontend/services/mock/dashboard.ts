/**
 * ==============================================================================
 * MOCK DASHBOARD SERVICE
 * ==============================================================================
 * DISCLAIMER:
 * Supplies realistic, internally consistent mock data for Phase 4 Dashboard UI.
 * - Reuses existing task models from `mockTaskService`.
 * - Contains all recommendation and risk heuristics here instead of the UI.
 * - Simulates asynchronous access with safe fallbacks and latency.
 * ==============================================================================
 */

import { mockTaskService } from "./tasks"
import type {
  Task,
  DashboardOverview,
  RecommendedTask,
  AtRiskTask,
  ScheduleBlock,
} from "@/types"

const simulateLatency = (ms: number = 200): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms))

/**
 * Retrieve high-level summary overview of today's schedule and task status.
 */
export async function getDashboardOverview(): Promise<DashboardOverview> {
  await simulateLatency(150)
  const tasks = await mockTaskService.getTasks()

  const pendingOrInProgress = tasks.filter(
    (t) => t.status === "pending" || t.status === "in_progress"
  )
  const completedToday = tasks.filter((t) => t.status === "completed")

  const totalEstimated = tasks.reduce((acc, t) => acc + t.estimatedDuration, 0)
  const totalCompleted = tasks.reduce((acc, t) => acc + t.completedDuration, 0)
  const overallProgress =
    totalEstimated > 0
      ? Math.min(100, Math.round((totalCompleted / totalEstimated) * 100))
      : 0

  const atRisk = await getAtRiskTasks()

  return {
    availableTimeHours: 6.0,
    scheduledWorkloadHours: 4.5,
    overallProgress,
    pendingTasksCount: pendingOrInProgress.length,
    atRiskTasksCount: atRisk.length,
    completedTodayCount: completedToday.length,
  }
}

/**
 * Retrieve the single highest-priority recommended next task with explanation.
 */
export async function getRecommendedTask(): Promise<RecommendedTask | null> {
  await simulateLatency(150)
  const tasks = await mockTaskService.getTasks()

  // 1. Prioritize DBMS task if not yet completed
  const dbmsTask = tasks.find(
    (t) =>
      t.title.toLowerCase().includes("dbms") && t.status !== "completed"
  )

  if (dbmsTask) {
    return {
      task: dbmsTask,
      recommendationReason:
        "Due tomorrow at 5:00 PM with 1h 30m estimated remaining. Completing this high-priority assignment during today's focus block prevents deadline risk cascade.",
      urgencyLabel: "Due Tomorrow",
    }
  }

  // 2. Fallback to active tasks sorted by priority and deadline
  const activeTasks = tasks.filter((t) => t.status !== "completed")
  if (activeTasks.length === 0) {
    return null
  }

  const priorityWeight: Record<string, number> = {
    critical: 4,
    high: 3,
    medium: 2,
    low: 1,
  }

  activeTasks.sort((a, b) => {
    const pDiff =
      (priorityWeight[b.priority] || 0) - (priorityWeight[a.priority] || 0)
    if (pDiff !== 0) return pDiff
    return (
      new Date(a.deadline).getTime() - new Date(b.deadline).getTime()
    )
  })

  const topTask = activeTasks[0]
  return {
    task: topTask,
    recommendationReason: `High priority item with ${topTask.remainingDuration}h remaining. Early focus preserves dynamic timeline buffers for upcoming deliverables.`,
    urgencyLabel:
      topTask.priority === "critical"
        ? "Critical Priority"
        : "Next in Queue",
  }
}

/**
 * Retrieve active upcoming tasks sorted chronologically by deadline.
 */
export async function getUpcomingDeadlines(): Promise<Task[]> {
  await simulateLatency(150)
  const tasks = await mockTaskService.getTasks()

  const active = tasks
    .filter((t) => t.status !== "completed")
    .sort(
      (a, b) =>
        new Date(a.deadline).getTime() - new Date(b.deadline).getTime()
    )

  return active.slice(0, 5)
}

/**
 * Retrieve tasks flagged as at-risk along with explicit rationale.
 */
export async function getAtRiskTasks(): Promise<AtRiskTask[]> {
  await simulateLatency(150)
  const tasks = await mockTaskService.getTasks()

  const atRiskList: AtRiskTask[] = []

  for (const t of tasks) {
    if (t.status === "overdue") {
      atRiskList.push({
        task: t,
        riskLevel: "critical",
        riskReason: `Deadline elapsed with ${t.remainingDuration}h remaining work. Immediate schedule rescheduling or deadline extension required.`,
      })
    } else if (
      t.status !== "completed" &&
      (t.id === "task-105" ||
        (t.priority === "critical" && t.remainingDuration >= 10))
    ) {
      atRiskList.push({
        task: t,
        riskLevel: "high",
        riskReason: `${t.remainingDuration}h remaining duration with insufficient daily allocation slots before final milestone.`,
      })
    }
  }

  return atRiskList
}

/**
 * Retrieve chronological schedule blocks for today.
 */
export async function getTodaySchedule(): Promise<ScheduleBlock[]> {
  await simulateLatency(150)
  const tasks = await mockTaskService.getTasks()

  const pipelineTask = tasks.find((t) => t.id === "task-101")
  const dbmsTask = tasks.find((t) => t.title.toLowerCase().includes("dbms"))
  const auditTask = tasks.find((t) => t.id === "task-102")
  const serializersTask = tasks.find((t) => t.id === "task-103")

  return [
    {
      id: "sched-1",
      startTime: "09:00 AM",
      endTime: "10:30 AM",
      title: pipelineTask
        ? pipelineTask.title
        : "Implement Core Data Ingestion Pipeline",
      category: pipelineTask?.category || "Engineering",
      taskId: pipelineTask?.id,
      status: "completed",
      durationMinutes: 90,
    },
    {
      id: "sched-2",
      startTime: "11:00 AM",
      endTime: "12:30 PM",
      title: dbmsTask
        ? dbmsTask.title
        : "DBMS Assignment: Query Optimization & Indexing",
      category: dbmsTask?.category || "Academics",
      taskId: dbmsTask?.id,
      status: dbmsTask?.status === "in_progress" ? "current" : "upcoming",
      durationMinutes: 90,
    },
    {
      id: "sched-3",
      startTime: "02:00 PM",
      endTime: "03:30 PM",
      title: auditTask
        ? auditTask.title
        : "Design Accessibility Audit for Form Controls",
      category: auditTask?.category || "Design",
      taskId: auditTask?.id,
      status: "upcoming",
      durationMinutes: 90,
    },
    {
      id: "sched-4",
      startTime: "04:30 PM",
      endTime: "05:30 PM",
      title: serializersTask
        ? serializersTask.title
        : "Refactor Legacy API Response Serializers",
      category: serializersTask?.category || "Engineering",
      taskId: serializersTask?.id,
      status: "upcoming",
      durationMinutes: 60,
    },
  ]
}

export const mockDashboardService = {
  getDashboardOverview,
  getRecommendedTask,
  getUpcomingDeadlines,
  getAtRiskTasks,
  getTodaySchedule,
}
