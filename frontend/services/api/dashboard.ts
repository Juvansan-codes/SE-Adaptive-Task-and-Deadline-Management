/**
 * Real Dashboard Service connected to FastAPI /api/dashboard endpoints.
 */

import { apiClient } from "./client"
import type {
  DashboardOverview,
  RecommendedTask,
  AtRiskTask,
  ScheduleBlock,
  Task,
} from "@/types"

export async function getDashboardOverview(): Promise<DashboardOverview> {
  return apiClient.get<DashboardOverview>("/dashboard/overview")
}

export async function getRecommendedTask(): Promise<RecommendedTask | null> {
  return apiClient.get<RecommendedTask | null>("/dashboard/recommendation")
}

export async function getUpcomingDeadlines(): Promise<Task[]> {
  return apiClient.get<Task[]>("/dashboard/upcoming")
}

export async function getAtRiskTasks(): Promise<AtRiskTask[]> {
  return apiClient.get<AtRiskTask[]>("/dashboard/at-risk")
}

export async function getTodaySchedule(): Promise<ScheduleBlock[]> {
  return apiClient.get<ScheduleBlock[]>("/dashboard/schedule")
}

export const dashboardService = {
  getDashboardOverview,
  getRecommendedTask,
  getUpcomingDeadlines,
  getAtRiskTasks,
  getTodaySchedule,
}
