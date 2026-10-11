import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  getSchedule,
  getRecommendedTask,
  getScheduleUpdate,
  dismissScheduleUpdate,
} from "@/services/mock/schedule"

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

export function useScheduleRecommendedTask() {
  return useQuery({
    queryKey: SCHEDULE_KEYS.recommended,
    queryFn: () => getRecommendedTask(),
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
