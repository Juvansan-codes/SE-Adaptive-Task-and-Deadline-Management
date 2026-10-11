"use client"

import * as React from "react"
import { format, parseISO, isValid } from "date-fns"
import { Calendar, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

interface DeadlineIndicatorProps {
  deadline: string
  showRelative?: boolean
  className?: string
  isCompleted?: boolean
}

const emptySubscribe = () => () => {}

export function DeadlineIndicator({
  deadline,
  showRelative = true,
  className,
  isCompleted = false,
}: DeadlineIndicatorProps) {
  // Safe client mounting check via useSyncExternalStore (React 19 compliant)
  const mounted = React.useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false
  )

  const date = React.useMemo(() => {
    try {
      const parsed = parseISO(deadline)
      return isValid(parsed) ? parsed : new Date(deadline)
    } catch {
      return null
    }
  }, [deadline])

  if (!date || !isValid(date)) {
    return <span className="text-xs text-muted-foreground">{deadline}</span>
  }

  const formattedDate = format(date, "MMM d, yyyy")

  // Only calculate time-sensitive comparisons on client after mount
  let overdue = false
  let dueToday = false
  let relativeText = ""

  if (mounted && !isCompleted) {
    const now = new Date()
    const isPast = date.getTime() < now.getTime()
    const isSameDay =
      date.getFullYear() === now.getFullYear() &&
      date.getMonth() === now.getMonth() &&
      date.getDate() === now.getDate()

    dueToday = isSameDay
    overdue = isPast && !isSameDay

    const diffMs = date.getTime() - now.getTime()
    const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24))

    if (dueToday) {
      relativeText = "Due today"
    } else if (overdue) {
      relativeText = `Overdue (${Math.abs(diffDays)}d ago)`
    } else if (diffDays === 1) {
      relativeText = "in 1 day"
    } else {
      relativeText = `in ${diffDays} days`
    }
  }

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 text-xs",
        overdue
          ? "text-red-600 dark:text-red-400 font-medium"
          : dueToday
          ? "text-orange-600 dark:text-orange-400 font-medium"
          : "text-muted-foreground",
        className
      )}
      title={`Deadline: ${formattedDate}`}
    >
      {overdue ? (
        <AlertTriangle className="size-3.5 shrink-0 text-red-500" />
      ) : (
        <Calendar className="size-3.5 shrink-0 text-muted-foreground" />
      )}
      <span>{formattedDate}</span>
      {showRelative && relativeText && (
        <span
          className={cn(
            "text-[11px]",
            overdue
              ? "text-red-500/90 font-normal"
              : dueToday
              ? "text-orange-600/90 font-semibold"
              : "text-muted-foreground/70"
          )}
        >
          ({relativeText})
        </span>
      )}
    </div>
  )
}
