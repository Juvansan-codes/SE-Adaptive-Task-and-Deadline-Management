/**
 * ==============================================================================
 * MOCK AVAILABILITY SERVICE
 * ==============================================================================
 * Manages weekly work/study availability schedule in memory.
 * - Simulates asynchronous access with latency.
 * - Stores availability state for all 7 days of the week.
 * ==============================================================================
 */

import type { WeeklyAvailability } from "@/types/settings"

const simulateLatency = (ms: number = 200): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms))

const DEFAULT_WEEKLY_AVAILABILITY: WeeklyAvailability = [
  {
    day: "monday",
    label: "Monday",
    enabled: true,
    startTime: "09:00",
    endTime: "17:00",
  },
  {
    day: "tuesday",
    label: "Tuesday",
    enabled: true,
    startTime: "09:00",
    endTime: "17:00",
  },
  {
    day: "wednesday",
    label: "Wednesday",
    enabled: true,
    startTime: "09:00",
    endTime: "17:00",
  },
  {
    day: "thursday",
    label: "Thursday",
    enabled: true,
    startTime: "09:00",
    endTime: "17:00",
  },
  {
    day: "friday",
    label: "Friday",
    enabled: true,
    startTime: "09:00",
    endTime: "16:00",
  },
  {
    day: "saturday",
    label: "Saturday",
    enabled: true,
    startTime: "10:00",
    endTime: "14:00",
  },
  {
    day: "sunday",
    label: "Sunday",
    enabled: false,
    startTime: "10:00",
    endTime: "14:00",
  },
]

let mockWeeklyAvailability: WeeklyAvailability = JSON.parse(
  JSON.stringify(DEFAULT_WEEKLY_AVAILABILITY)
)

export async function getWeeklyAvailability(): Promise<WeeklyAvailability> {
  await simulateLatency(150)
  return JSON.parse(JSON.stringify(mockWeeklyAvailability))
}

export async function updateWeeklyAvailability(
  availability: WeeklyAvailability
): Promise<WeeklyAvailability> {
  await simulateLatency(250)
  mockWeeklyAvailability = JSON.parse(JSON.stringify(availability))
  return JSON.parse(JSON.stringify(mockWeeklyAvailability))
}

export async function resetWeeklyAvailability(): Promise<WeeklyAvailability> {
  await simulateLatency(150)
  mockWeeklyAvailability = JSON.parse(JSON.stringify(DEFAULT_WEEKLY_AVAILABILITY))
  return JSON.parse(JSON.stringify(mockWeeklyAvailability))
}

export const mockAvailabilityService = {
  getWeeklyAvailability,
  updateWeeklyAvailability,
  resetWeeklyAvailability,
}
