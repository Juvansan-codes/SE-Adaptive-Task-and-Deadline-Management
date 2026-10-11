import * as React from "react"
import Link from "next/link"
import { LayoutDashboard, Plus, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { EmptyState } from "@/components/common/empty-state"

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex flex-col gap-1.5 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground md:text-2xl">
            Dashboard
          </h1>
          <p className="text-sm text-muted-foreground">
            Overview of adaptive scheduling, priorities, and deadlines.
          </p>
        </div>
        <div className="flex items-center gap-2 pt-2 md:pt-0">
          <Badge variant="outline" className="text-xs">
            Phase 1
          </Badge>
          <Link href="/tasks">
            <Button variant="primary" size="sm">
              <Plus className="size-3.5" />
              <span>New Task</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Main Restrained Placeholder State */}
      <div className="rounded-lg border border-border bg-card p-6 shadow-2xs">
        <EmptyState
          icon={LayoutDashboard}
          title="No active dashboard metrics"
          description="Adaptive insights, workload velocity, and deadline forecasts will populate here as tasks are tracked."
          action={
            <div className="flex flex-wrap items-center justify-center gap-2">
              <Link href="/tasks">
                <Button variant="primary" size="sm">
                  <span>Go to Tasks</span>
                  <ArrowRight className="size-3.5" />
                </Button>
              </Link>
              <Link href="/schedule">
                <Button variant="outline" size="sm">
                  <span>View Schedule</span>
                </Button>
              </Link>
            </div>
          }
        />
      </div>
    </div>
  )
}
