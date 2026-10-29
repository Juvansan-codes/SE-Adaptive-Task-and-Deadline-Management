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
          <h1 className="text-2xl font-semibold tracking-[-0.025em] leading-[1.2] text-foreground">
            Schedule
          </h1>
          {schedule?.isToday && (
            <Badge variant="outline" className="text-xs rounded-[6px]">
              Today
            </Badge>
          )}
        </div>
        <p className="mt-0.5 text-sm text-muted-foreground font-normal">
          {formattedDate}
        </p>
      </div>

      {/* Controls & Quick Actions */}
      <div className="flex flex-wrap items-center gap-2 pt-1 md:pt-0">
        {/* Date Selector Navigation */}
        <div className="flex h-9 items-center rounded-[6px] border border-border bg-card p-0.5 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onPrevDay}
            className="size-7 rounded-[4px]"
            aria-label="Previous day"
          >
            <ChevronLeft className="size-3.5" />
          </Button>
          <span className="px-2 text-xs font-medium text-foreground">
            {schedule?.dayOfWeek || "Monday"}
          </span>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onNextDay}
            className="size-7 rounded-[4px]"
            aria-label="Next day"
          >
            <ChevronRight className="size-3.5" />
          </Button>
        </div>

        {/* Capacity Capsule */}
        <div className="hidden sm:flex h-9 items-center rounded-[6px] border border-border bg-card px-3 text-xs text-muted-foreground shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
          <span className="font-semibold text-foreground font-mono tabular-nums mr-1">
            {scheduledHours}h
          </span>
          <span>/</span>
          <span className="font-mono tabular-nums ml-1">
            {availableHours}h capacity
          </span>
        </div>

        {/* Refresh */}
        {onRefresh && (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onRefresh}
            className="size-9 rounded-[6px] text-muted-foreground hover:text-foreground"
            title="Refresh schedule"
          >
            <RotateCcw className="size-3.5" />
          </Button>
        )}

        {/* New Task Link */}
        <Link href="/tasks">
          <Button variant="primary" size="default" className="h-9 px-3 text-[13px] rounded-[6px] gap-1.5">
            <Plus className="size-3.5" />
            <span>New Task</span>
          </Button>
        </Link>
      </div>
    </div>
  )
}
