"use client"

import * as React from "react"
import { toast } from "sonner"
import { Calendar, Save, RotateCcw, AlertTriangle } from "lucide-react"

import type { DayAvailability, WeeklyAvailability } from "@/types/settings"
import { Button } from "@/components/ui/button"
import { AvailabilityDayRow } from "./availability-day-row"
import {
  useWeeklyAvailability,
  useUpdateWeeklyAvailability,
  useResetWeeklyAvailability,
} from "@/hooks/use-settings"
import { LoadingState } from "@/components/common/loading-state"
import { ErrorState } from "@/components/common/error-state"

interface AvailabilityFormProps {
  initialAvailability: WeeklyAvailability
}

function AvailabilityForm({ initialAvailability }: AvailabilityFormProps) {
  const updateMutation = useUpdateWeeklyAvailability()
  const resetMutation = useResetWeeklyAvailability()

  const [availability, setAvailability] = React.useState<WeeklyAvailability>(
    () => JSON.parse(JSON.stringify(initialAvailability))
  )
  const [hasChanges, setHasChanges] = React.useState(false)

  // Validate entire weekly configuration
  const invalidDays = React.useMemo(() => {
    return availability.filter((d) => {
      if (!d.enabled) return false
      if (!d.startTime || !d.endTime) return true
      return d.startTime >= d.endTime
    })
  }, [availability])

  const isValid = invalidDays.length === 0

  // Calculate total weekly hours
  const totalWeeklyHours = React.useMemo(() => {
    return availability.reduce((acc, d) => {
      if (!d.enabled || !d.startTime || !d.endTime || d.startTime >= d.endTime) {
        return acc
      }
      const [startH, startM] = d.startTime.split(":").map(Number)
      const [endH, endM] = d.endTime.split(":").map(Number)
      const minutes = endH * 60 + endM - (startH * 60 + startM)
      return acc + minutes / 60
    }, 0)
  }, [availability])

  const activeDaysCount = availability.filter((d) => d.enabled).length

  const handleDayChange = (updatedDay: DayAvailability) => {
    setAvailability((prev) =>
      prev.map((d) => (d.day === updatedDay.day ? updatedDay : d))
    )
    setHasChanges(true)
  }

  const handleSave = async () => {
    if (!isValid) {
      toast.error("Invalid availability configuration", {
        description: `Please fix end times for: ${invalidDays.map((d) => d.label).join(", ")}.`,
      })
      return
    }

    try {
      await updateMutation.mutateAsync(availability)
      setHasChanges(false)
      toast.success("Availability updated successfully", {
        description: `Configured ${totalWeeklyHours.toFixed(1)}h across ${activeDaysCount} active days.`,
      })
    } catch {
      toast.error("Failed to save availability settings.")
    }
  }

  const handleReset = async () => {
    try {
      const reset = await resetMutation.mutateAsync()
      setAvailability(JSON.parse(JSON.stringify(reset)))
      setHasChanges(false)
      toast.info("Availability reset to default schedule.")
    } catch {
      toast.error("Failed to reset availability.")
    }
  }

  const handleSetWeekdaysStandard = () => {
    setAvailability((prev) =>
      prev.map((d) => {
        if (d.day === "saturday" || d.day === "sunday") {
          return { ...d, enabled: false }
        }
        return {
          ...d,
          enabled: true,
          startTime: "09:00",
          endTime: "17:00",
        }
      })
    )
    setHasChanges(true)
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Top Banner / Summary Card */}
      <div className="flex flex-col gap-4 rounded-lg border border-border bg-card p-5 shadow-2xs sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-md border border-border bg-muted/40 text-foreground">
            <Calendar className="size-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-foreground">
              Weekly Study &amp; Work Hours
            </h2>
            <p className="text-xs text-muted-foreground">
              Configure available focus windows for dynamic deadline allocation.
            </p>
          </div>
        </div>

        {/* Total Capacity Metric Capsule */}
        <div className="flex flex-wrap items-center gap-3 border-t border-border/60 pt-3 sm:border-t-0 sm:pt-0">
          <div className="flex flex-col sm:items-end">
            <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
              Weekly Capacity
            </span>
            <span className="text-base font-bold tracking-tight text-foreground tabular-nums">
              {totalWeeklyHours.toFixed(1)}h
              <span className="text-xs font-normal text-muted-foreground ml-1">
                ({activeDaysCount} days active)
              </span>
            </span>
          </div>
        </div>
      </div>

      {/* Validation Warning Callout */}
      {!isValid && (
        <div className="flex items-start gap-2.5 rounded-md border border-red-200 bg-red-50 p-3 text-xs text-red-800 dark:border-red-900/40 dark:bg-red-950/20 dark:text-red-300">
          <AlertTriangle className="size-4 shrink-0 mt-0.5 text-red-600 dark:text-red-400" />
          <div>
            <span className="font-semibold">Invalid Time Slots Detected:</span>{" "}
            {invalidDays.map((d) => d.label).join(", ")} must have end times
            strictly after start times before saving.
          </div>
        </div>
      )}

      {/* Presets and Quick Actions */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleSetWeekdaysStandard}
            className="text-xs h-7"
          >
            Apply Standard (M–F 9–5)
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleReset}
            disabled={resetMutation.isPending}
            className="text-xs h-7 text-muted-foreground hover:text-foreground"
          >
            <RotateCcw className="size-3 mr-1" />
            <span>Reset Defaults</span>
          </Button>
        </div>

        {hasChanges && (
          <span className="text-xs text-orange-600 dark:text-orange-400 font-medium">
            Unsaved changes
          </span>
        )}
      </div>

      {/* Day by Day List */}
      <div className="flex flex-col gap-2.5">
        {availability.map((dayConfig) => (
          <AvailabilityDayRow
            key={dayConfig.day}
            dayConfig={dayConfig}
            onChange={handleDayChange}
          />
        ))}
      </div>

      {/* Save Button Footer */}
      <div className="flex items-center justify-end gap-3 border-t border-border/80 pt-4">
        <Button
          type="button"
          variant="primary"
          size="sm"
          onClick={handleSave}
          disabled={!isValid || updateMutation.isPending || !hasChanges}
          className="gap-1.5"
        >
          {updateMutation.isPending ? (
            <span>Saving...</span>
          ) : (
            <>
              <Save className="size-3.5" />
              <span>Save Availability</span>
            </>
          )}
        </Button>
      </div>
    </div>
  )
}

export function AvailabilityEditor() {
  const {
    data: initialAvailability,
    isLoading,
    isError,
    refetch,
  } = useWeeklyAvailability()

  if (isLoading) {
    return (
      <div className="rounded-lg border border-border bg-card p-8 shadow-2xs">
        <LoadingState message="Loading weekly availability settings..." />
      </div>
    )
  }

  if (isError || !initialAvailability) {
    return (
      <div className="rounded-lg border border-border bg-card p-6 shadow-2xs">
        <ErrorState
          title="Failed to load availability"
          message="Unable to retrieve weekly working hours from the service."
          onRetry={() => refetch()}
        />
      </div>
    )
  }

  return <AvailabilityForm initialAvailability={initialAvailability} />
}
