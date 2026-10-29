"use client"

import * as React from "react"
import Link from "next/link"
import { Plus, Calendar, RotateCcw, Sparkles } from "lucide-react"
import { toast } from "sonner"
import { useSeedTasks } from "@/hooks/use-tasks"

import { Button } from "@/components/ui/button"
import { ErrorState } from "@/components/common/error-state"
import {
  useDashboardOverview,
  useRecommendedTask,
  useUpcomingDeadlines,
  useAtRiskTasks,
  useTodaySchedule,
} from "@/hooks/use-dashboard"
import {
  OverviewStats,
  RecommendedTask,
  UpcomingDeadlines,
  AtRiskTasks,
  TodaySchedule,
} from "@/components/dashboard"

export default function DashboardPage() {
  const seedTasks = useSeedTasks()
  const {
    data: overview,
    isLoading: isOverviewLoading,
    isError: isOverviewError,
    refetch: refetchOverview,
  } = useDashboardOverview()

  const {
    data: recommended,
    isLoading: isRecommendedLoading,
    isError: isRecommendedError,
    refetch: refetchRecommended,
  } = useRecommendedTask()

  const {
    data: upcomingDeadlines,
    isLoading: isUpcomingLoading,
    isError: isUpcomingError,
    refetch: refetchUpcoming,
  } = useUpcomingDeadlines()

  const {
    data: atRiskTasks,
    isLoading: isAtRiskLoading,
    isError: isAtRiskError,
    refetch: refetchAtRisk,
  } = useAtRiskTasks()

  const {
    data: todaySchedule,
    isLoading: isScheduleLoading,
    isError: isScheduleError,
    refetch: refetchSchedule,
  } = useTodaySchedule()

  const hasCriticalError =
    isOverviewError &&
    isRecommendedError &&
    isUpcomingError &&
    isAtRiskError &&
    isScheduleError

  const handleRetryAll = () => {
    refetchOverview()
    refetchRecommended()
    refetchUpcoming()
    refetchAtRisk()
    refetchSchedule()
  }

  if (hasCriticalError) {
    return (
      <div className="flex flex-col gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-[-0.025em] leading-[1.2] text-foreground">
            Dashboard
          </h1>
          <p className="mt-1 text-sm font-normal text-muted-foreground">
            Adaptive daily overview, recommended priorities, and timeline forecast.
          </p>
        </div>
        <ErrorState
          title="Failed to load dashboard metrics"
          message="Unable to retrieve active tasks and adaptive schedule forecasts from the service."
          onRetry={handleRetryAll}
        />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Page Header */}
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-[-0.025em] leading-[1.2] text-foreground">
            Dashboard
          </h1>
          <p className="mt-0.5 text-sm font-normal text-muted-foreground">
            Adaptive daily overview, recommended priorities, and timeline forecast.
          </p>
        </div>
        <div className="flex items-center gap-2 pt-1 md:pt-0">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={handleRetryAll}
            className="size-9 rounded-[6px] text-muted-foreground hover:text-foreground"
            title="Refresh dashboard data"
          >
            <RotateCcw className="size-3.5" />
          </Button>
          {overview && overview.pendingTasksCount === 0 && overview.completedTodayCount === 0 && (
            <Button
              variant="outline"
              size="default"
              disabled={seedTasks.isPending}
              onClick={async () => {
                try {
                  await seedTasks.mutateAsync()
                  handleRetryAll()
                  toast.success("Loaded sample starter tasks!")
                } catch {
                  toast.error("Failed to load sample tasks.")
                }
              }}
              title="Populate workspace with sample tasks"
              className="h-9 px-3 text-[13px] rounded-[6px] gap-1.5"
            >
              <Sparkles className="size-3.5 text-primary" />
              <span>{seedTasks.isPending ? "Loading..." : "Load Sample Tasks"}</span>
            </Button>
          )}
          <Link href="/schedule">
            <Button variant="outline" size="default" className="h-9 px-3 text-[13px] rounded-[6px] gap-1.5">
              <Calendar className="size-3.5" />
              <span>Schedule</span>
            </Button>
          </Link>
          <Link href="/tasks">
            <Button variant="primary" size="default" className="h-9 px-3 text-[13px] rounded-[6px] gap-1.5">
              <Plus className="size-3.5" />
              <span>New Task</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* A. Today's Overview Stats */}
      <OverviewStats overview={overview} isLoading={isOverviewLoading} />

      {/* Main Grid: Left Column for Primary Workload & Deadlines, Right Column for Schedule Preview */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        {/* Left Column (8 cols): Primary Focus + Critical Lists */}
        <div className="flex flex-col gap-4 lg:col-span-7 xl:col-span-8">
          {/* B. Recommended Next Task */}
          <RecommendedTask
            recommended={recommended}
            isLoading={isRecommendedLoading}
          />

          {/* D. At-Risk Tasks */}
          <AtRiskTasks
            atRiskTasks={atRiskTasks}
            isLoading={isAtRiskLoading}
          />

          {/* C. Upcoming Deadlines */}
          <UpcomingDeadlines
            tasks={upcomingDeadlines}
            isLoading={isUpcomingLoading}
          />
        </div>

        {/* Right Column (4-5 cols): Schedule & Timeline Context */}
        <div className="flex flex-col gap-4 lg:col-span-5 xl:col-span-4">
          {/* E. Today's Schedule */}
          <TodaySchedule
            schedule={todaySchedule}
            isLoading={isScheduleLoading}
          />
        </div>
      </div>
    </div>
  )
}
