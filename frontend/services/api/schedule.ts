/**
 * Real Schedule Service connected to FastAPI /api/schedule endpoints.
 */

import { apiClient } from "./client"
import type { DaySchedule, ScheduleItem, ScheduleUpdate } from "@/types"

/**
 * Retrieve the active day's schedule timeline for requested date (or today in user timezone).
 */
export async function getSchedule(date?: string): Promise<DaySchedule> {
  const params: Record<string, string | undefined> = {}
  if (date && date.trim()) {
    params.date = date.trim()
  }
  return apiClient.get<DaySchedule>("/schedule", { params })
}

/**
 * Retrieve the recommended task item from the active day's schedule.
 */
export async function getRecommendedTask(date?: string): Promise<ScheduleItem | null> {
  const schedule = await getSchedule(date)
  const item = schedule.items.find((i) => i.isRecommended)
  return item ? { ...item } : null
}

/**
 * Retrieve pending adaptive schedule update notification if available.
 */
export async function getScheduleUpdate(): Promise<ScheduleUpdate | null> {
  return apiClient.get<ScheduleUpdate | null>("/schedule/update")
}

/**
 * Dismiss or acknowledge the schedule update banner.
 */
export async function dismissScheduleUpdate(): Promise<boolean> {
  await apiClient.post("/schedule/update/dismiss")
  return true
}

/**
 * Regenerate schedule dynamically using current database records.
 */
export async function regenerateSchedule(date?: string): Promise<DaySchedule> {
  return apiClient.post<DaySchedule>("/schedule/regenerate", {
    date: date || undefined,
  })
}

export const scheduleService = {
  getSchedule,
  getRecommendedTask,
  getScheduleUpdate,
  dismissScheduleUpdate,
  regenerateSchedule,
}
