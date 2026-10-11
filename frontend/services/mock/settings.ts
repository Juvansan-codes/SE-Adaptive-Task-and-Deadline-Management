/**
 * ==============================================================================
 * MOCK SETTINGS SERVICE
 * ==============================================================================
 * Manages user profile and preferences in memory.
 * - Simulates asynchronous access with latency.
 * - Stores profile, notification preferences, and task buffers.
 * ==============================================================================
 */

import type { UserProfile, UserPreferences } from "@/types/settings"
import {
  getWeeklyAvailability,
  updateWeeklyAvailability,
  resetWeeklyAvailability,
} from "./availability"

const simulateLatency = (ms: number = 200): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms))

const DEFAULT_PROFILE: UserProfile = {
  id: "usr_alex_01",
  name: "Alex Mercer",
  email: "alex.mercer@example.com",
  timezone: "UTC-05:00 (Eastern Time)",
  role: "Engineering Student",
}

const DEFAULT_PREFERENCES: UserPreferences = {
  enableDeadlineReminders: true,
  enableScheduleUpdates: true,
  defaultTaskDurationMinutes: 60,
  dailyFocusHoursLimit: 6.5,
  bufferStrategy: "moderate",
}

let mockProfile: UserProfile = { ...DEFAULT_PROFILE }
let mockPreferences: UserPreferences = { ...DEFAULT_PREFERENCES }

export async function getProfile(): Promise<UserProfile> {
  await simulateLatency(150)
  return { ...mockProfile }
}

export async function updateProfile(
  updates: Partial<UserProfile>
): Promise<UserProfile> {
  await simulateLatency(250)
  mockProfile = {
    ...mockProfile,
    ...updates,
    name: updates.name ? updates.name.trim() : mockProfile.name,
    email: updates.email ? updates.email.trim().toLowerCase() : mockProfile.email,
  }
  return { ...mockProfile }
}

export async function getPreferences(): Promise<UserPreferences> {
  await simulateLatency(150)
  return { ...mockPreferences }
}

export async function updatePreferences(
  updates: Partial<UserPreferences>
): Promise<UserPreferences> {
  await simulateLatency(250)
  mockPreferences = {
    ...mockPreferences,
    ...updates,
  }
  return { ...mockPreferences }
}

export const mockSettingsService = {
  getProfile,
  updateProfile,
  getPreferences,
  updatePreferences,
  getWeeklyAvailability,
  updateWeeklyAvailability,
  resetWeeklyAvailability,
}
