import * as React from "react"
import { Badge } from "@/components/ui/badge"
import type { TaskDifficulty } from "@/types/task"
import { cn } from "@/lib/utils"

interface DifficultyBadgeProps {
  difficulty: TaskDifficulty
  className?: string
}

export function DifficultyBadge({ difficulty, className }: DifficultyBadgeProps) {
  const config: Record<TaskDifficulty, { label: string; style: string }> = {
    hard: {
      label: "Hard",
      style: "border-red-200/80 bg-red-50/60 text-red-700 dark:border-red-900/40 dark:bg-red-950/30 dark:text-red-400",
    },
    medium: {
      label: "Medium",
      style: "border-amber-200/80 bg-amber-50/60 text-amber-700 dark:border-amber-900/40 dark:bg-amber-950/30 dark:text-amber-400",
    },
    easy: {
      label: "Easy",
      style: "border-emerald-200/80 bg-emerald-50/60 text-emerald-700 dark:border-emerald-900/40 dark:bg-emerald-950/30 dark:text-emerald-400",
    },
  }

  const { label, style } = config[difficulty] || config.medium

  return (
    <Badge
      variant="outline"
      className={cn("px-2 py-0.5 text-[11px] font-normal", style, className)}
    >
      <span>{label}</span>
    </Badge>
  )
}
