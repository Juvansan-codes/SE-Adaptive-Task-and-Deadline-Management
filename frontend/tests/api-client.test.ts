/**
 * Automated tests for Frontend API Client and Services
 * Uses native node:test, node:assert, and tsx
 */

import test from "node:test"
import assert from "node:assert/strict"

// Mock global fetch
let lastFetchUrl = ""
let lastFetchOptions: RequestInit = {}
let mockResponseStatus = 200
let mockResponseBody: unknown = {}
let mockResponseHeaders: Record<string, string> = { "content-type": "application/json" }
let networkFailureMode = false

globalThis.fetch = (async (url: RequestInfo | URL, options: RequestInit = {}) => {
  lastFetchUrl = url.toString()
  lastFetchOptions = options

  if (networkFailureMode) {
    throw new Error("Failed to fetch")
  }

  return {
    status: mockResponseStatus,
    ok: mockResponseStatus >= 200 && mockResponseStatus < 300,
    headers: {
      get: (header: string) => mockResponseHeaders[header.toLowerCase()] || null,
    },
    json: async () => mockResponseBody,
    text: async () => JSON.stringify(mockResponseBody),
  } as unknown as Response
}) as typeof globalThis.fetch

// Set required dummy environment variables
process.env.NEXT_PUBLIC_API_URL = "http://localhost:8000/api"
process.env.NEXT_PUBLIC_SUPABASE_URL = "https://mock.supabase.co"
process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = "mock-anon-key"

// Import API client and services
import { apiClient, ApiClientError } from "../services/api/client"
import { taskService } from "../services/api/tasks"
import { dashboardService } from "../services/api/dashboard"
import { scheduleService } from "../services/api/schedule"
import { settingsService } from "../services/api/settings"
import { availabilityService } from "../services/api/availability"

test("API Client: sends GET request with Accept header and query parameters", async () => {
  mockResponseStatus = 200
  mockResponseBody = [{ id: "task-01", title: "Test Task" }]

  const data = await apiClient.get<Array<{ id: string; title: string }>>("/tasks", {
    params: { status: "pending", limit: 10 },
  })

  assert.equal(data.length, 1)
  assert.equal(data[0].title, "Test Task")
  assert.match(lastFetchUrl, /\/api\/tasks\?status=pending&limit=10/)
  assert.equal(lastFetchOptions.method, "GET")
  assert.equal(new Headers(lastFetchOptions.headers).get("Accept"), "application/json")
})

test("API Client: sends POST request with Content-Type header and JSON body", async () => {
  mockResponseStatus = 201
  mockResponseBody = { id: "task-new", title: "New Task" }

  const payload = { title: "New Task", category: "General" }
  const data = await apiClient.post<{ id: string; title: string }>("/tasks", payload)

  assert.equal(data.id, "task-new")
  assert.equal(lastFetchOptions.method, "POST")
  assert.equal(new Headers(lastFetchOptions.headers).get("Content-Type"), "application/json")
  assert.equal(lastFetchOptions.body, JSON.stringify(payload))
})

test("API Client: handles 204 No Content empty response cleanly", async () => {
  mockResponseStatus = 204
  mockResponseBody = null

  const data = await apiClient.delete("/tasks/task-01")
  assert.deepEqual(data, {})
})

test("API Client: extracts error message from FastAPI detail dict", async () => {
  mockResponseStatus = 400
  mockResponseBody = { detail: { status: "error", message: "Time window start must precede end" } }

  await assert.rejects(
    async () => {
      await apiClient.put("/settings/availability", [])
    },
    (err: unknown) => {
      assert.ok(err instanceof ApiClientError)
      assert.equal(err.status, 400)
      assert.equal(err.message, "Time window start must precede end")
      return true
    }
  )
})

test("API Client: extracts error message from Pydantic validation errors", async () => {
  mockResponseStatus = 422
  mockResponseBody = {
    detail: [
      {
        loc: ["body", "daily_focus_hours_limit"],
        msg: "Input should be less than or equal to 24",
      },
    ],
  }

  await assert.rejects(
    async () => {
      await apiClient.patch("/settings/preferences", { dailyFocusHoursLimit: 30 })
    },
    (err: unknown) => {
      assert.ok(err instanceof ApiClientError)
      assert.equal(err.status, 422)
      assert.match(err.message, /Input should be less than or equal to 24/)
      return true
    }
  )
})

test("API Client: handles network connectivity failure safely", async () => {
  networkFailureMode = true

  await assert.rejects(
    async () => {
      await apiClient.get("/dashboard/overview")
    },
    (err: unknown) => {
      assert.ok(err instanceof ApiClientError)
      assert.equal(err.status, 0)
      assert.match(err.message, /Unable to connect to the backend server/)
      return true
    }
  )

  networkFailureMode = false
})

test("Task Service: filters ignore 'all' parameters and map sort parameters", async () => {
  mockResponseStatus = 200
  mockResponseBody = []

  await taskService.getTasks({
    status: "all",
    priority: "critical",
    category: "all",
    sortBy: "deadline",
    sortDirection: "desc",
    search: "algorithms",
  })

  // 'all' values must NOT be appended to query params
  assert.ok(!lastFetchUrl.includes("status=all"))
  assert.ok(!lastFetchUrl.includes("category=all"))
  assert.ok(lastFetchUrl.includes("priority=critical"))
  assert.ok(lastFetchUrl.includes("sort_by=deadline"))
  assert.ok(lastFetchUrl.includes("sort_order=desc"))
  assert.ok(lastFetchUrl.includes("search=algorithms"))
})

test("Dashboard Service: calls proper overview, recommendation, and risk routes", async () => {
  mockResponseStatus = 200
  mockResponseBody = { availableTimeHours: 6.5, scheduledWorkloadHours: 2.0 }

  await dashboardService.getDashboardOverview()
  assert.ok(lastFetchUrl.endsWith("/api/dashboard/overview"))

  await dashboardService.getRecommendedTask()
  assert.ok(lastFetchUrl.endsWith("/api/dashboard/recommendation"))

  await dashboardService.getAtRiskTasks()
  assert.ok(lastFetchUrl.endsWith("/api/dashboard/at-risk"))

  await dashboardService.getUpcomingDeadlines()
  assert.ok(lastFetchUrl.endsWith("/api/dashboard/upcoming"))

  await dashboardService.getTodaySchedule()
  assert.ok(lastFetchUrl.endsWith("/api/dashboard/schedule"))
})

test("Schedule Service: calls schedule and regenerate endpoints", async () => {
  mockResponseStatus = 200
  mockResponseBody = { date: "2026-10-20", items: [] }

  await scheduleService.getSchedule("2026-10-20")
  assert.ok(lastFetchUrl.includes("/api/schedule?date=2026-10-20"))

  await scheduleService.regenerateSchedule("2026-10-20")
  assert.ok(lastFetchUrl.endsWith("/api/schedule/regenerate"))
  assert.equal(lastFetchOptions.method, "POST")
  assert.equal(lastFetchOptions.body, JSON.stringify({ date: "2026-10-20" }))

  await scheduleService.getScheduleUpdate()
  assert.ok(lastFetchUrl.endsWith("/api/schedule/update"))

  await scheduleService.dismissScheduleUpdate()
  assert.ok(lastFetchUrl.endsWith("/api/schedule/update/dismiss"))
})

test("Settings & Availability Services: calls profile, preferences, and availability reset", async () => {
  mockResponseStatus = 200
  mockResponseBody = []

  await availabilityService.getWeeklyAvailability()
  assert.ok(lastFetchUrl.endsWith("/api/settings/availability"))

  await availabilityService.resetWeeklyAvailability()
  assert.ok(lastFetchUrl.endsWith("/api/settings/availability/reset"))
  assert.equal(lastFetchOptions.method, "POST")

  await settingsService.getProfile()
  assert.ok(lastFetchUrl.endsWith("/api/settings/profile"))

  await settingsService.getPreferences()
  assert.ok(lastFetchUrl.endsWith("/api/settings/preferences"))
})
