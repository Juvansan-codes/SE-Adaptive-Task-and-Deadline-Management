import * as React from "react"
import { Clock, CheckCircle2, AlertCircle, PlayCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import type { TaskStatus } from "@/types/task"
import { cn } from "@/lib/utils"

interface StatusBadgeProps {
  status: TaskStatus
  className?: string
  showIcon?: boolean
}

export function StatusBadge({
  status,
  className,
  showIcon = true,
}: StatusBadgeProps) {
  const config: Record<
    TaskStatus,
    { label: string; icon: React.ComponentType<{ className?: string }>; style: string }
  > = {
    pending: {
      label: "Pending",
      icon: Clock,
      style: "border-neutral-200 bg-neutral-100 text-neutral-700 dark:border-neutral-800 dark:bg-neutral-800 dark:text-neutral-300",
    },
    in_progress: {
      label: "In Progress",
      icon: PlayCircle,
      style: "border-orange-200 bg-orange-50 text-orange-700 dark:border-orange-900/50 dark:bg-orange-950/40 dark:text-orange-400 font-medium",
    },
    completed: {
      label: "Completed",
      icon: CheckCircle2,
      style: "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900/50 dark:bg-emerald-950/40 dark:text-emerald-400 font-medium",
    },
    overdue: {
      label: "Overdue",
      icon: AlertCircle,
      style: "border-red-200 bg-red-50 text-red-700 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-400 font-semibold",
    },
  }

  const { label, icon: Icon, style } = config[status] || config.pending

  return (
    <Badge
      variant="outline"
      className={cn("inline-flex items-center gap-1 px-2 py-0.5 text-[11px]", style, className)}
    >
      {showIcon && <Icon className="size-3 shrink-0" />}
      <span>{label}</span>
    </Badge>
  )
}
