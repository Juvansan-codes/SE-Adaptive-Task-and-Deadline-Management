"use client"

import * as React from "react"
import { toast } from "sonner"

import { LoadingState } from "@/components/common/loading-state"
import { ErrorState } from "@/components/common/error-state"
import {
  ScheduleHeader,
  ScheduleUpdateBanner,
  TimelineView,
} from "@/components/schedule"
import {
  useSchedule,
  useScheduleUpdate,
  useDismissScheduleUpdate,
} from "@/hooks/use-schedule"

export default function SchedulePage() {
  const [currentDate] = React.useState("2026-10-12")

  const {
    data: schedule,
    isLoading: isScheduleLoading,
    isError: isScheduleError,
    refetch: refetchSchedule,
  } = useSchedule(currentDate)

  const {
    data: update,
    refetch: refetchUpdate,
  } = useScheduleUpdate()

  const dismissUpdateMutation = useDismissScheduleUpdate()

  const handleRefresh = () => {
    refetchSchedule()
    refetchUpdate()
    toast.success("Schedule refreshed", {
      description: "Timeline up to date with latest adaptive parameters.",
    })
  }

  const handleViewSchedule = () => {
    const el = document.getElementById("schedule-timeline")
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" })
    }
  }

  const handleDismissUpdate = () => {
    dismissUpdateMutation.mutate()
  }

  if (isScheduleLoading) {
    return (
      <div className="flex flex-col gap-6">
        <ScheduleHeader />
        <div className="rounded-lg border border-border bg-card p-12 shadow-2xs">
          <LoadingState
            message="Loading timeline schedule..."
            description="Generating dynamic focus blocks and timeline forecast."
          />
        </div>
      </div>
    )
  }

  if (isScheduleError || !schedule) {
    return (
      <div className="flex flex-col gap-6">
        <ScheduleHeader />
        <ErrorState
          title="Failed to load schedule"
          message="Unable to retrieve active timeline sessions from the mock service."
          onRetry={() => refetchSchedule()}
        />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Page Header */}
      <ScheduleHeader
        schedule={schedule}
        onRefresh={handleRefresh}
      />

      {/* Schedule Updated Banner if update data is available */}
      {update && (
        <ScheduleUpdateBanner
          update={update}
          onViewSchedule={handleViewSchedule}
          onDismiss={handleDismissUpdate}
        />
      )}

      {/* Timeline View */}
      <TimelineView schedule={schedule} />
    </div>
  )
}
