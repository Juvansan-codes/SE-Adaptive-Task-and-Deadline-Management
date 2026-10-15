/**
 * Real Availability Service connected to FastAPI /api/settings/availability endpoints.
 */

import { apiClient } from "./client"
import type { WeeklyAvailability } from "@/types/settings"

export async function getWeeklyAvailability(): Promise<WeeklyAvailability> {
  return apiClient.get<WeeklyAvailability>("/settings/availability")
}

export async function updateWeeklyAvailability(
  availability: WeeklyAvailability
): Promise<WeeklyAvailability> {
  return apiClient.put<WeeklyAvailability>("/settings/availability", availability)
}

export async function resetWeeklyAvailability(): Promise<WeeklyAvailability> {
  return apiClient.post<WeeklyAvailability>("/settings/availability/reset")
}

export const availabilityService = {
  getWeeklyAvailability,
  updateWeeklyAvailability,
  resetWeeklyAvailability,
}
