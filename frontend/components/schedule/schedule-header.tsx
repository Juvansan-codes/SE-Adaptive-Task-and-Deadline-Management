"use client"

import * as React from "react"
import Link from "next/link"
import { ChevronLeft, ChevronRight, Plus, RotateCcw } from "lucide-react"

import type { DaySchedule } from "@/types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface ScheduleHeaderProps {
  schedule?: DaySchedule
  onRefresh?: () => void
  onPrevDay?: () => void
  onNextDay?: () => void
  className?: string
}

export function ScheduleHeader({
  schedule,
  onRefresh,
  onPrevDay,
  onNextDay,
}: ScheduleHeaderProps) {
  const formattedDate = schedule?.formattedDate || "Monday, October 12, 2026"
  const scheduledHours = schedule?.totalScheduledHours || 5.5
  const availableHours = schedule?.availableHours || 6.5

  return (
    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      {/* Title & Date Heading */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-semibold tracking-tight text-foreground md:text-2xl">
            Schedule
          </h1>
          {schedule?.isToday && (
            <Badge variant="outline" className="text-xs">
              Today
            </Badge>
          )}
        </div>
        <p className="mt-0.5 text-sm text-muted-foreground font-medium">
          {formattedDate}
        </p>
      </div>

      {/* Controls & Quick Actions */}
      <div className="flex flex-wrap items-center gap-2 pt-1 md:pt-0">
        {/* Date Selector Navigation */}
        <div className="flex items-center rounded-md border border-border bg-card p-0.5 shadow-2xs">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onPrevDay}
            className="size-7"
            aria-label="Previous day"
          >
            <ChevronLeft className="size-3.5" />
          </Button>
          <span className="px-2 text-xs font-medium text-foreground tabular-nums">
            {schedule?.dayOfWeek || "Monday"}
          </span>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onNextDay}
            className="size-7"
            aria-label="Next day"
          >
            <ChevronRight className="size-3.5" />
          </Button>
        </div>

        {/* Capacity Capsule */}
        <div className="hidden sm:flex items-center rounded-md border border-border bg-card px-2.5 py-1 text-xs text-muted-foreground shadow-2xs">
          <span className="font-medium text-foreground tabular-nums mr-1">
            {scheduledHours}h
          </span>
          <span>/</span>
          <span className="tabular-nums ml-1">
            {availableHours}h capacity
          </span>
        </div>

        {/* Refresh */}
        {onRefresh && (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onRefresh}
            className="size-8 text-muted-foreground hover:text-foreground"
            title="Refresh schedule"
          >
            <RotateCcw className="size-3.5" />
          </Button>
        )}

        {/* New Task Link */}
        <Link href="/tasks">
          <Button variant="primary" size="sm">
            <Plus className="size-3.5" />
            <span>New Task</span>
          </Button>
        </Link>
      </div>
    </div>
  )
}
