import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  getWeeklyAvailability,
  updateWeeklyAvailability,
  resetWeeklyAvailability,
} from "@/services/mock/availability"
import {
  getProfile,
  updateProfile,
  getPreferences,
  updatePreferences,
} from "@/services/mock/settings"
import type {
  WeeklyAvailability,
  UserProfile,
  UserPreferences,
} from "@/types/settings"

export const SETTINGS_KEYS = {
  all: ["settings"] as const,
  availability: ["settings", "availability"] as const,
  profile: ["settings", "profile"] as const,
  preferences: ["settings", "preferences"] as const,
}

export function useWeeklyAvailability() {
  return useQuery({
    queryKey: SETTINGS_KEYS.availability,
    queryFn: () => getWeeklyAvailability(),
  })
}

export function useUpdateWeeklyAvailability() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (newAvailability: WeeklyAvailability) =>
      updateWeeklyAvailability(newAvailability),
    onSuccess: (data) => {
      queryClient.setQueryData(SETTINGS_KEYS.availability, data)
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.availability })
    },
  })
}

export function useResetWeeklyAvailability() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => resetWeeklyAvailability(),
    onSuccess: (data) => {
      queryClient.setQueryData(SETTINGS_KEYS.availability, data)
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.availability })
    },
  })
}

export function useProfile() {
  return useQuery({
    queryKey: SETTINGS_KEYS.profile,
    queryFn: () => getProfile(),
  })
}

export function useUpdateProfile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (updates: Partial<UserProfile>) => updateProfile(updates),
    onSuccess: (data) => {
      queryClient.setQueryData(SETTINGS_KEYS.profile, data)
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.profile })
    },
  })
}

export function usePreferences() {
  return useQuery({
    queryKey: SETTINGS_KEYS.preferences,
    queryFn: () => getPreferences(),
  })
}

export function useUpdatePreferences() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (updates: Partial<UserPreferences>) =>
      updatePreferences(updates),
    onSuccess: (data) => {
      queryClient.setQueryData(SETTINGS_KEYS.preferences, data)
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.preferences })
    },
  })
}
