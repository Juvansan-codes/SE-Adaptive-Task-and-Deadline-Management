import type { Task } from "./task"

export interface DashboardOverview {
  availableTimeHours: number
  scheduledWorkloadHours: number
  overallProgress: number
  pendingTasksCount: number
  atRiskTasksCount: number
  completedTodayCount: number
}

export interface RecommendedTask {
  task: Task
  recommendationReason: string
  urgencyLabel?: string
}

export interface AtRiskTask {
  task: Task
  riskLevel: "critical" | "high" | "moderate"
  riskReason: string
}

export interface ScheduleBlock {
  id: string
  startTime: string
  endTime: string
  title: string
  category: string
  taskId?: string
  status: "completed" | "current" | "upcoming"
  durationMinutes: number
}
