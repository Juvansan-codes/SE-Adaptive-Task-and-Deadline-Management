import * as React from "react"
import { CheckSquare, Plus, Filter } from "lucide-react"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/common/empty-state"

export default function TasksPage() {
  return (
    <div className="flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex flex-col gap-1.5 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground md:text-2xl">
            Tasks
          </h1>
          <p className="text-sm text-muted-foreground">
            Manage workload, prioritize objectives, and track deadline progress.
          </p>
        </div>
        <div className="flex items-center gap-2 pt-2 md:pt-0">
          <Button variant="outline" size="sm" disabled>
            <Filter className="size-3.5" />
            <span>Filter</span>
          </Button>
          <Button variant="primary" size="sm">
            <Plus className="size-3.5" />
            <span>Create Task</span>
          </Button>
        </div>
      </div>

      {/* Main Restrained Placeholder State */}
      <div className="rounded-lg border border-border bg-card p-6 shadow-2xs">
        <EmptyState
          icon={CheckSquare}
          title="No tasks created yet"
          description="Start by defining your objectives and target completion dates. The adaptive engine will calibrate your schedule accordingly."
          action={
            <Button variant="primary" size="sm">
              <Plus className="size-3.5" />
              <span>Create Task</span>
            </Button>
          }
        />
      </div>
    </div>
  )
}
