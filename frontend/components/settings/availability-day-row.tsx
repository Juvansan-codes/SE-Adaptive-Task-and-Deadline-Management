"use client"

import * as React from "react"
import { Clock, AlertCircle } from "lucide-react"

import type { DayAvailability } from "@/types/settings"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

interface AvailabilityDayRowProps {
  dayConfig: DayAvailability
  onChange: (updated: DayAvailability) => void
  className?: string
}

export function AvailabilityDayRow({
  dayConfig,
  onChange,
  className,
}: AvailabilityDayRowProps) {
  const { day, label, enabled, startTime, endTime } = dayConfig

  // Validate that end time is after start time when enabled
  const isValidTime = React.useMemo(() => {
    if (!enabled) return true
    if (!startTime || !endTime) return false
    return startTime < endTime
  }, [enabled, startTime, endTime])

  // Calculate day duration in hours
  const durationHours = React.useMemo(() => {
    if (!enabled || !isValidTime || !startTime || !endTime) return 0
    const [startH, startM] = startTime.split(":").map(Number)
    const [endH, endM] = endTime.split(":").map(Number)
    const totalMinutes = endH * 60 + endM - (startH * 60 + startM)
    return Math.max(0, Number((totalMinutes / 60).toFixed(1)))
  }, [enabled, isValidTime, startTime, endTime])

  const handleToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({
      ...dayConfig,
      enabled: e.target.checked,
    })
  }

  const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({
      ...dayConfig,
      startTime: e.target.value,
    })
  }

  const handleEndTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({
      ...dayConfig,
      endTime: e.target.value,
    })
  }

  return (
    <div
      className={cn(
        "flex flex-col gap-3 rounded-lg border border-border bg-card p-3.5 transition-colors sm:flex-row sm:items-center sm:justify-between",
        !enabled && "bg-neutral-50/50 opacity-70 dark:bg-neutral-900/30",
        !isValidTime && enabled && "border-red-300 bg-red-50/20 dark:border-red-900/40 dark:bg-red-950/10",
        className
      )}
    >
      {/* Day label and toggle */}
      <div className="flex items-center gap-3 sm:w-44">
        <label
          htmlFor={`toggle-${day}`}
          className="relative inline-flex cursor-pointer items-center"
        >
          <input
            type="checkbox"
            id={`toggle-${day}`}
            checked={enabled}
            onChange={handleToggle}
            className="peer sr-only"
            aria-label={`Enable availability for ${label}`}
          />
          <div className="h-5 w-9 rounded-full bg-neutral-200 peer-focus-visible:ring-2 peer-focus-visible:ring-primary peer-focus-visible:ring-offset-2 peer-checked:bg-primary transition-colors after:absolute after:top-[2px] after:left-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full dark:bg-neutral-700" />
        </label>

        <div className="flex flex-col">
          <label
            htmlFor={`toggle-${day}`}
            className="cursor-pointer text-sm font-semibold tracking-tight text-foreground select-none"
          >
            {label}
          </label>
          <span className="text-[11px] text-muted-foreground">
            {enabled ? (
              <span className="text-emerald-600 dark:text-emerald-400 font-medium">
                Active ({durationHours}h)
              </span>
            ) : (
              "Unavailable"
            )}
          </span>
        </div>
      </div>

      {/* Time inputs and status */}
      <div className="flex flex-1 flex-wrap items-center gap-2 sm:justify-end">
        {enabled ? (
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5">
              <label
                htmlFor={`start-${day}`}
                className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider"
              >
                From
              </label>
              <Input
                type="time"
                id={`start-${day}`}
                value={startTime}
                onChange={handleStartTimeChange}
                disabled={!enabled}
                className={cn(
                  "h-8 w-28 text-xs tabular-nums",
                  !isValidTime && "border-red-500 focus-visible:ring-red-500"
                )}
                aria-label={`${label} start time`}
              />
            </div>

            <div className="flex items-center gap-1.5">
              <label
                htmlFor={`end-${day}`}
                className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider"
              >
                To
              </label>
              <Input
                type="time"
                id={`end-${day}`}
                value={endTime}
                onChange={handleEndTimeChange}
                disabled={!enabled}
                className={cn(
                  "h-8 w-28 text-xs tabular-nums",
                  !isValidTime && "border-red-500 focus-visible:ring-red-500"
                )}
                aria-label={`${label} end time`}
              />
            </div>

            <div className="hidden lg:flex items-center gap-1 text-xs text-muted-foreground tabular-nums w-14 justify-end">
              <Clock className="size-3 text-muted-foreground/70" />
              <span>{durationHours}h</span>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-[11px] text-muted-foreground">
              Off Day
            </Badge>
          </div>
        )}
      </div>

      {/* Error message if invalid */}
      {!isValidTime && enabled && (
        <div className="flex items-center gap-1.5 text-xs text-red-600 dark:text-red-400 sm:w-full sm:pt-1">
          <AlertCircle className="size-3.5 shrink-0" />
          <span>End time must be after start time.</span>
        </div>
      )}
    </div>
  )
}
