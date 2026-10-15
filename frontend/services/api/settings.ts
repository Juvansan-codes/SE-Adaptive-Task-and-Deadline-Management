/**
 * Real Settings Service connected to FastAPI /api/settings endpoints.
 */

import { apiClient } from "./client"
import type { UserProfile, UserPreferences, SettingsState } from "@/types/settings"
import {
  getWeeklyAvailability,
  updateWeeklyAvailability,
  resetWeeklyAvailability,
} from "./availability"

export async function getProfile(): Promise<UserProfile> {
  return apiClient.get<UserProfile>("/settings/profile")
}

export async function updateProfile(
  updates: Partial<UserProfile>
): Promise<UserProfile> {
  return apiClient.patch<UserProfile>("/settings/profile", updates)
}

export async function getPreferences(): Promise<UserPreferences> {
  return apiClient.get<UserPreferences>("/settings/preferences")
}

export async function updatePreferences(
  updates: Partial<UserPreferences>
): Promise<UserPreferences> {
  return apiClient.patch<UserPreferences>("/settings/preferences", updates)
}

export async function getSettingsState(): Promise<SettingsState> {
  return apiClient.get<SettingsState>("/settings")
}

export async function updateSettings(
  updates: Partial<SettingsState>
): Promise<SettingsState> {
  return apiClient.patch<SettingsState>("/settings", updates)
}

export const settingsService = {
  getProfile,
  updateProfile,
  getPreferences,
  updatePreferences,
  getWeeklyAvailability,
  updateWeeklyAvailability,
  resetWeeklyAvailability,
  getSettingsState,
  updateSettings,
}
