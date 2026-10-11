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
