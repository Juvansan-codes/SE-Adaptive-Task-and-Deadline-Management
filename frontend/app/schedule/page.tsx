import * as React from "react"
import { Calendar, ChevronLeft, ChevronRight, SlidersHorizontal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/common/empty-state"

export default function SchedulePage() {
  return (
    <div className="flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex flex-col gap-1.5 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground md:text-2xl">
            Schedule
          </h1>
          <p className="text-sm text-muted-foreground">
            Dynamic timeline forecasting and adaptive deadline adjustments.
          </p>
        </div>
        <div className="flex items-center gap-2 pt-2 md:pt-0">
          <div className="flex items-center rounded-md border border-border bg-background p-0.5">
            <Button variant="ghost" size="icon-sm" className="size-7" disabled aria-label="Previous period">
              <ChevronLeft className="size-3.5" />
            </Button>
            <span className="px-2 text-xs font-medium text-muted-foreground">Current Week</span>
            <Button variant="ghost" size="icon-sm" className="size-7" disabled aria-label="Next period">
              <ChevronRight className="size-3.5" />
            </Button>
          </div>
          <Button variant="outline" size="sm" disabled>
            <SlidersHorizontal className="size-3.5" />
            <span>Preferences</span>
          </Button>
        </div>
      </div>

      {/* Main Restrained Placeholder State */}
      <div className="rounded-lg border border-border bg-card p-6 shadow-2xs">
        <EmptyState
          icon={Calendar}
          title="Schedule timeline empty"
          description="Your adaptive timeline will automatically generate once tasks with assigned durations and deadlines are created."
          action={
            <Button variant="primary" size="sm">
              <span>Configure Schedule</span>
            </Button>
          }
        />
      </div>
    </div>
  )
}
