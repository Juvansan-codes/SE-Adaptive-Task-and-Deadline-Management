import * as React from "react"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"

interface ProgressBarProps {
  progress: number
  completedDuration?: number
  estimatedDuration?: number
  showLabel?: boolean
  className?: string
  size?: "sm" | "default"
}

export function ProgressBar({
  progress,
  completedDuration,
  estimatedDuration,
  showLabel = true,
  className,
  size = "default",
}: ProgressBarProps) {
  const safeProgress = Math.min(100, Math.max(0, Math.round(progress)))

  return (
    <div className={cn("flex flex-col gap-1 w-full", className)}>
      {showLabel && (
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-medium text-foreground">{safeProgress}%</span>
          {completedDuration !== undefined && estimatedDuration !== undefined && (
            <span className="tabular-nums">
              {completedDuration}h / {estimatedDuration}h
            </span>
          )}
        </div>
      )}
      <div className={cn("w-full", size === "sm" ? "[&_[data-slot=progress-track]]:h-1" : "[&_[data-slot=progress-track]]:h-1.5")}>
        <Progress value={safeProgress} className="w-full" />
      </div>
    </div>
  )
}
