import { useQuery } from "@tanstack/react-query"
import {
  getDashboardOverview,
  getRecommendedTask,
  getUpcomingDeadlines,
  getAtRiskTasks,
  getTodaySchedule,
} from "@/services/mock/dashboard"

export const DASHBOARD_KEYS = {
  all: ["dashboard"] as const,
  overview: ["dashboard", "overview"] as const,
  recommended: ["dashboard", "recommended"] as const,
  upcoming: ["dashboard", "upcoming"] as const,
  atRisk: ["dashboard", "at-risk"] as const,
  schedule: ["dashboard", "schedule"] as const,
}

export function useDashboardOverview() {
  return useQuery({
    queryKey: DASHBOARD_KEYS.overview,
    queryFn: () => getDashboardOverview(),
  })
}

export function useRecommendedTask() {
  return useQuery({
    queryKey: DASHBOARD_KEYS.recommended,
    queryFn: () => getRecommendedTask(),
  })
}

export function useUpcomingDeadlines() {
  return useQuery({
    queryKey: DASHBOARD_KEYS.upcoming,
    queryFn: () => getUpcomingDeadlines(),
  })
}

export function useAtRiskTasks() {
  return useQuery({
    queryKey: DASHBOARD_KEYS.atRisk,
    queryFn: () => getAtRiskTasks(),
  })
}

export function useTodaySchedule() {
  return useQuery({
    queryKey: DASHBOARD_KEYS.schedule,
    queryFn: () => getTodaySchedule(),
  })
}
