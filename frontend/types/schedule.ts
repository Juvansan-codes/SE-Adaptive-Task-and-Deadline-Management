import type { TaskPriority } from "./task"

export type ScheduleItemStatus = "pending" | "in_progress" | "completed" | "overdue"

export interface ScheduleItem {
  id: string
  taskId?: string
  title: string
  category: string
  startTime: string
  endTime: string
  durationMinutes: number
  status: ScheduleItemStatus
  isRecommended?: boolean
  recommendationReason?: string
  priority?: TaskPriority
  notes?: string
}

export interface DaySchedule {
  date: string
  dayOfWeek: string
  formattedDate: string
  isToday: boolean
  items: ScheduleItem[]
  totalScheduledHours: number
  availableHours: number
}

export interface ScheduleUpdate {
  id: string
  title: string
  timestamp: string
  summary?: string
  changes: string[]
  recommendedAction?: string
}

export type DisruptionType = "lost_time" | "task_overrun"
export type RecoveryStrategyType = "buffer_absorption" | "workload_triage" | "deadline_extension"

export interface SimulationDisruptionInput {
  disruptionType: DisruptionType
  targetDate?: string
  hoursLost?: number
  overrunTaskId?: string
  additionalHours?: number
}

export interface CascadingBreachItem {
  taskId: string
  title: string
  category: string
  priority: TaskPriority
  deadline: string
  remainingDuration: number
  delayHours: number
  breachMagnitudeHours: number
  riskLevel: "critical" | "high" | "moderate"
  explanation: string
}

export interface RecoveryStrategy {
  id: string
  strategyType: RecoveryStrategyType
  title: string
  description: string
  badge: string
  feasibilityScore: number
  stressIndex: "low" | "moderate" | "high"
  deadlinesSavedCount: number
  isRecommended: boolean
  changesSummary: string[]
  actionPayload: Record<string, any>
}

export interface DisruptionSimulationResult {
  disruptionType: DisruptionType
  hoursDisrupted: number
  targetDate: string
  baselineFeasibilityPct: number
  disruptedFeasibilityPct: number
  breachedTasksCount: number
  breachedTasks: CascadingBreachItem[]
  strategies: RecoveryStrategy[]
  simulationTimestamp: string
}

export interface ApplyStrategyRequest {
  strategyId: string
  strategyType: RecoveryStrategyType
  actionPayload: Record<string, any>
  targetDate?: string
}

export interface ApplyStrategyResponse {
  success: boolean
  message: string
  appliedStrategyName: string
  changesApplied: string[]
}
