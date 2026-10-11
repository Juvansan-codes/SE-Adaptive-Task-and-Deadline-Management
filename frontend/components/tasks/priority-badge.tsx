import * as React from "react"
import { AlertOctagon, AlertTriangle, ArrowUp, ArrowDown } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import type { TaskPriority } from "@/types/task"
import { cn } from "@/lib/utils"

interface PriorityBadgeProps {
  priority: TaskPriority
  className?: string
  showIcon?: boolean
}

export function PriorityBadge({
  priority,
  className,
  showIcon = true,
}: PriorityBadgeProps) {
  const config: Record<
    TaskPriority,
    { label: string; icon: React.ComponentType<{ className?: string }>; style: string }
  > = {
    critical: {
      label: "Critical",
      icon: AlertOctagon,
      style: "border-red-200 bg-red-50 text-red-700 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-400 font-semibold",
    },
    high: {
      label: "High",
      icon: AlertTriangle,
      style: "border-orange-200 bg-orange-50 text-orange-700 dark:border-orange-900/50 dark:bg-orange-950/40 dark:text-orange-400 font-medium",
    },
    medium: {
      label: "Medium",
      icon: ArrowUp,
      style: "border-neutral-200 bg-neutral-100 text-neutral-700 dark:border-neutral-800 dark:bg-neutral-800 dark:text-neutral-300 font-medium",
    },
    low: {
      label: "Low",
      icon: ArrowDown,
      style: "border-neutral-200 bg-neutral-50 text-neutral-600 dark:border-neutral-800/60 dark:bg-neutral-900 dark:text-neutral-400",
    },
  }

  const { label, icon: Icon, style } = config[priority] || config.medium

  return (
    <Badge
      variant="outline"
      className={cn("inline-flex items-center gap-1 px-2 py-0.5 text-[11px]", style, className)}
    >
      {showIcon && <Icon className="size-3" />}
      <span>{label}</span>
    </Badge>
  )
}
