import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  getSchedule,
  getRecommendedTask,
  getScheduleUpdate,
  dismissScheduleUpdate,
  regenerateSchedule,
} from "@/services/api/schedule"

export const SCHEDULE_KEYS = {
  all: ["schedule"] as const,
  day: (date?: string) => ["schedule", "day", date] as const,
  recommended: ["schedule", "recommended"] as const,
  update: ["schedule", "update"] as const,
}

export function useSchedule(date?: string) {
  return useQuery({
    queryKey: SCHEDULE_KEYS.day(date),
    queryFn: () => getSchedule(date),
  })
}

export function useScheduleRecommendedTask(date?: string) {
  return useQuery({
    queryKey: SCHEDULE_KEYS.recommended,
    queryFn: () => getRecommendedTask(date),
  })
}

export function useScheduleUpdate() {
  return useQuery({
    queryKey: SCHEDULE_KEYS.update,
    queryFn: () => getScheduleUpdate(),
  })
}

export function useDismissScheduleUpdate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => dismissScheduleUpdate(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SCHEDULE_KEYS.update })
    },
  })
}

export function useRegenerateSchedule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (date?: string) => regenerateSchedule(date),
    onSuccess: (_, date) => {
      queryClient.invalidateQueries({ queryKey: SCHEDULE_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      if (date) {
        queryClient.invalidateQueries({ queryKey: SCHEDULE_KEYS.day(date) })
      }
    },
  })
}
