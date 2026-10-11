/**
 * ==============================================================================
 * MOCK SCHEDULE SERVICE
 * ==============================================================================
 * DISCLAIMER:
 * Supplies realistic, internally consistent mock schedule data for Phase 5 UI.
 * - Simulates asynchronous API requests with artificial latency.
 * - Encapsulates all schedule generation and state heuristics outside UI components.
 * - Provides recommended, completed, overdue, and scheduled timeline items.
 * ==============================================================================
 */

import type { DaySchedule, ScheduleItem, ScheduleUpdate } from "@/types"

const simulateLatency = (ms: number = 200): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms))

const INITIAL_SCHEDULE_ITEMS: ScheduleItem[] = [
  {
    id: "item-01",
    taskId: "task-104",
    title: "Setup CI/CD Automated Lint & Type-Check Gates",
    category: "DevOps",
    startTime: "09:00 AM",
    endTime: "10:15 AM",
    durationMinutes: 75,
    status: "completed",
    priority: "medium",
    notes: "Pipeline workflows configured with GitHub Actions and branch protection rules.",
  },
  {
    id: "item-02",
    taskId: "task-108",
    title: "DBMS Assignment: Query Optimization & Indexing",
    category: "Academics",
    startTime: "10:30 AM",
    endTime: "12:00 PM",
    durationMinutes: 90,
    status: "in_progress",
    priority: "high",
    isRecommended: true,
    recommendationReason:
      "Due tomorrow with 1h 30m remaining. Completing this high-priority assignment during today's focus block prevents deadline risk cascade.",
    notes: "Focus on B-tree index execution plan comparisons and query cost analysis.",
  },
  {
    id: "item-03",
    taskId: "task-103",
    title: "Refactor Legacy API Response Serializers",
    category: "Engineering",
    startTime: "01:00 PM",
    endTime: "02:30 PM",
    durationMinutes: 90,
    status: "overdue",
    priority: "high",
    notes:
      "Original milestone elapsed with 5.0h unfinished work. Rescheduled catch-up block to unblock downstream integration.",
  },
  {
    id: "item-04",
    taskId: "task-102",
    title: "Design Accessibility Audit for Form Controls",
    category: "Design",
    startTime: "02:45 PM",
    endTime: "04:15 PM",
    durationMinutes: 90,
    status: "pending",
    priority: "high",
    notes: "WCAG 2.1 AA keyboard focus, contrast ratios, and screen-reader aria labels.",
  },
  {
    id: "item-05",
    taskId: "task-105",
    title: "Draft Adaptive Scheduling Heuristic Specifications",
    category: "Product",
    startTime: "04:30 PM",
    endTime: "05:30 PM",
    durationMinutes: 60,
    status: "pending",
    priority: "critical",
    notes: "Define timeline displacement constraints, buffer formulas, and priority weighting.",
  },
]

const INITIAL_SCHEDULE_UPDATE: ScheduleUpdate = {
  id: "update-101",
  title: "Schedule Updated",
  timestamp: "10 minutes ago",
  summary: "Adaptive engine automatically adjusted your focus blocks following recent progress updates.",
  changes: [
    "2 tasks were moved to accommodate focus capacity",
    "1 task was reprioritized to prevent deadline risk cascade",
  ],
  recommendedAction: "View Updated Schedule",
}

const mockScheduleItems: ScheduleItem[] = [...INITIAL_SCHEDULE_ITEMS]
let mockScheduleUpdate: ScheduleUpdate | null = { ...INITIAL_SCHEDULE_UPDATE }

/**
 * Retrieve the active day's schedule timeline.
 */
export async function getSchedule(date?: string): Promise<DaySchedule> {
  await simulateLatency(150)

  const activeDate = date || "2026-10-12"
  const totalMinutes = mockScheduleItems.reduce(
    (acc, item) => acc + item.durationMinutes,
    0
  )
  const totalScheduledHours = Number((totalMinutes / 60).toFixed(1))

  return {
    date: activeDate,
    dayOfWeek: "Monday",
    formattedDate: "Monday, October 12, 2026",
    isToday: true,
    items: [...mockScheduleItems],
    totalScheduledHours,
    availableHours: 6.5,
  }
}

/**
 * Retrieve the recommended task in the schedule.
 */
export async function getRecommendedTask(): Promise<ScheduleItem | null> {
  await simulateLatency(100)
  const item = mockScheduleItems.find((i) => i.isRecommended)
  return item ? { ...item } : null
}

/**
 * Retrieve pending schedule update notification if available.
 */
export async function getScheduleUpdate(): Promise<ScheduleUpdate | null> {
  await simulateLatency(100)
  return mockScheduleUpdate ? { ...mockScheduleUpdate } : null
}

/**
 * Dismiss or acknowledge the schedule update banner.
 */
export async function dismissScheduleUpdate(): Promise<boolean> {
  await simulateLatency(100)
  mockScheduleUpdate = null
  return true
}

export const mockScheduleService = {
  getSchedule,
  getRecommendedTask,
  getScheduleUpdate,
  dismissScheduleUpdate,
}
