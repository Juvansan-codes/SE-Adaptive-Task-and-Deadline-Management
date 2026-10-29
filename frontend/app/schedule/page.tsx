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
  const [currentDate, setCurrentDate] = React.useState<string>(() => {
    const today = new Date()
    return today.toISOString().split("T")[0]
  })

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

  const handlePrevDay = () => {
    const d = new Date(currentDate)
    d.setDate(d.getDate() - 1)
    setCurrentDate(d.toISOString().split("T")[0])
  }

  const handleNextDay = () => {
    const d = new Date(currentDate)
    d.setDate(d.getDate() + 1)
    setCurrentDate(d.toISOString().split("T")[0])
  }

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
        <ScheduleHeader onPrevDay={handlePrevDay} onNextDay={handleNextDay} />
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
        <ScheduleHeader onPrevDay={handlePrevDay} onNextDay={handleNextDay} />
        <ErrorState
          title="Failed to load schedule"
          message="Unable to retrieve active timeline sessions from the adaptive service."
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
        onPrevDay={handlePrevDay}
        onNextDay={handleNextDay}
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
