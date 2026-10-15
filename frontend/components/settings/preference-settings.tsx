"use client"

import * as React from "react"
import { toast } from "sonner"
import { Bell, Sliders, Save } from "lucide-react"

import type { UserPreferences } from "@/types/settings"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { usePreferences, useUpdatePreferences } from "@/hooks/use-settings"
import { LoadingState } from "@/components/common/loading-state"
import { ErrorState } from "@/components/common/error-state"

const DURATION_OPTIONS = [
  { value: "30", label: "30 minutes (Quick Session)" },
  { value: "45", label: "45 minutes (Pomodoro Block)" },
  { value: "60", label: "60 minutes (1 Hour Focus)" },
  { value: "90", label: "90 minutes (1.5 Hours Deep Work)" },
  { value: "120", label: "120 minutes (2 Hours Extended)" },
]

interface PreferenceFormProps {
  initialPreferences: UserPreferences
}

function PreferenceForm({ initialPreferences }: PreferenceFormProps) {
  const updateMutation = useUpdatePreferences()

  const [preferences, setPreferences] = React.useState<UserPreferences>(() => ({
    ...initialPreferences,
  }))
  const [hasChanges, setHasChanges] = React.useState(false)

  const handleToggle = (key: "enableDeadlineReminders" | "enableScheduleUpdates") => {
    setPreferences((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
    setHasChanges(true)
  }

  const handleDurationChange = (val: string | null) => {
    if (!val) return
    setPreferences((prev) => ({
      ...prev,
      defaultTaskDurationMinutes: Number(val),
    }))
    setHasChanges(true)
  }

  const handleFocusLimitChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value) || 0
    setPreferences((prev) => ({
      ...prev,
      dailyFocusHoursLimit: Math.max(1, Math.min(16, val)),
    }))
    setHasChanges(true)
  }

  const handleBufferStrategyChange = (
    val: "tight" | "moderate" | "relaxed" | null
  ) => {
    if (!val) return
    setPreferences((prev) => ({
      ...prev,
      bufferStrategy: val,
    }))
    setHasChanges(true)
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await updateMutation.mutateAsync(preferences)
      setHasChanges(false)
      toast.success("Preferences updated successfully", {
        description: "Adaptive scheduling heuristics will respect these parameters.",
      })
    } catch {
      toast.error("Failed to update preferences.")
    }
  }

  return (
    <form onSubmit={handleSave} className="flex flex-col gap-6">
      {/* Scheduling Preferences */}
      <div className="flex flex-col gap-5 rounded-lg border border-border bg-card p-5 shadow-2xs">
        <div className="flex items-start gap-3">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-md border border-border bg-muted/40 text-foreground">
            <Sliders className="size-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-foreground">
              Scheduling Parameters
            </h2>
            <p className="text-xs text-muted-foreground">
              Define default estimation durations, daily focus capacity limits, and timeline buffers.
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 pt-2">
          {/* Default Task Duration */}
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="default-duration"
              className="text-xs font-medium text-foreground"
            >
              Default Task Duration
            </label>
            <Select
              value={preferences.defaultTaskDurationMinutes.toString()}
              onValueChange={handleDurationChange}
            >
              <SelectTrigger id="default-duration" className="w-full">
                <SelectValue placeholder="Select duration..." />
              </SelectTrigger>
              <SelectContent>
                {DURATION_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <span className="text-[11px] text-muted-foreground">
              Pre-filled duration applied when creating new tasks.
            </span>
          </div>

          {/* Daily Focus Limit */}
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="focus-limit"
              className="text-xs font-medium text-foreground"
            >
              Daily Focus Target (Hours)
            </label>
            <Input
              id="focus-limit"
              type="number"
              min={1}
              max={16}
              step={0.5}
              value={preferences.dailyFocusHoursLimit}
              onChange={handleFocusLimitChange}
              className="tabular-nums"
            />
            <span className="text-[11px] text-muted-foreground">
              Upper bound for daily scheduled sessions before warning of cognitive overload.
            </span>
          </div>

          {/* Buffer Strategy */}
          <div className="flex flex-col gap-1.5 sm:col-span-2">
            <label
              htmlFor="buffer-strategy"
              className="text-xs font-medium text-foreground"
            >
              Adaptive Buffer Strategy
            </label>
            <Select
              value={preferences.bufferStrategy}
              onValueChange={handleBufferStrategyChange}
            >
              <SelectTrigger id="buffer-strategy" className="w-full max-w-md">
                <SelectValue placeholder="Select strategy..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="tight">Strict (10% Buffer — aggressive deadlines)</SelectItem>
                <SelectItem value="moderate">Moderate (20% Buffer — balanced pacing)</SelectItem>
                <SelectItem value="relaxed">Conservative (35% Buffer — high protection)</SelectItem>
              </SelectContent>
            </Select>
            <span className="text-[11px] text-muted-foreground">
              Determines how much safety margin the scheduler reserves before hard deadlines.
            </span>
          </div>
        </div>
      </div>

      {/* Notification Preferences */}
      <div className="flex flex-col gap-4 rounded-lg border border-border bg-card p-5 shadow-2xs">
        <div className="flex items-start gap-3">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-md border border-border bg-muted/40 text-foreground">
            <Bell className="size-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-foreground">
              Notification Preferences
            </h2>
            <p className="text-xs text-muted-foreground">
              Configure alert triggers for upcoming deadlines and timeline updates.
            </p>
          </div>
        </div>

        <div className="flex flex-col divide-y divide-border/60 pt-1">
          {/* Deadline Reminders Toggle */}
          <div className="flex items-center justify-between py-3">
            <div className="flex flex-col pr-4">
              <span className="text-xs font-medium text-foreground">
                Deadline Reminders
              </span>
              <span className="text-[11px] text-muted-foreground">
                Receive proactive warnings when tasks are approaching deadline or at risk of slipping.
              </span>
            </div>
            <label
              htmlFor="toggle-deadline-reminders"
              className="relative inline-flex cursor-pointer items-center shrink-0"
            >
              <input
                type="checkbox"
                id="toggle-deadline-reminders"
                checked={preferences.enableDeadlineReminders}
                onChange={() => handleToggle("enableDeadlineReminders")}
                className="peer sr-only"
                aria-label="Enable deadline reminders"
              />
              <div className="h-5 w-9 rounded-full bg-neutral-200 peer-focus-visible:ring-2 peer-focus-visible:ring-primary peer-focus-visible:ring-offset-2 peer-checked:bg-primary transition-colors after:absolute after:top-[2px] after:left-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full dark:bg-neutral-700" />
            </label>
          </div>

          {/* Schedule Update Banners Toggle */}
          <div className="flex items-center justify-between py-3">
            <div className="flex flex-col pr-4">
              <span className="text-xs font-medium text-foreground">
                Schedule Adaptation Notifications
              </span>
              <span className="text-[11px] text-muted-foreground">
                Show banners when the adaptive engine reprioritizes or shifts sessions.
              </span>
            </div>
            <label
              htmlFor="toggle-schedule-updates"
              className="relative inline-flex cursor-pointer items-center shrink-0"
            >
              <input
                type="checkbox"
                id="toggle-schedule-updates"
                checked={preferences.enableScheduleUpdates}
                onChange={() => handleToggle("enableScheduleUpdates")}
                className="peer sr-only"
                aria-label="Enable schedule adaptation notifications"
              />
              <div className="h-5 w-9 rounded-full bg-neutral-200 peer-focus-visible:ring-2 peer-focus-visible:ring-primary peer-focus-visible:ring-offset-2 peer-checked:bg-primary transition-colors after:absolute after:top-[2px] after:left-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full dark:bg-neutral-700" />
            </label>
          </div>
        </div>
      </div>

      {/* Save Button Footer */}
      <div className="flex items-center justify-between border-t border-border/80 pt-4">
        {hasChanges ? (
          <span className="text-xs text-orange-600 dark:text-orange-400 font-medium">
            Unsaved preference changes
          </span>
        ) : (
          <span className="text-xs text-muted-foreground">
            Preferences up to date
          </span>
        )}
        <Button
          type="submit"
          variant="primary"
          size="sm"
          disabled={updateMutation.isPending || !hasChanges}
          className="gap-1.5"
        >
          {updateMutation.isPending ? (
            <span>Saving...</span>
          ) : (
            <>
              <Save className="size-3.5" />
              <span>Save Preferences</span>
            </>
          )}
        </Button>
      </div>
    </form>
  )
}

export function PreferenceSettings() {
  const { data: initialPreferences, isLoading, isError, refetch } = usePreferences()

  if (isLoading) {
    return (
      <div className="rounded-lg border border-border bg-card p-8 shadow-2xs">
        <LoadingState message="Loading preferences..." />
      </div>
    )
  }

  if (isError || !initialPreferences) {
    return (
      <div className="rounded-lg border border-border bg-card p-6 shadow-2xs">
        <ErrorState
          title="Failed to load preferences"
          message="Unable to retrieve user preferences. Please check your connection."
          onRetry={() => refetch()}
        />
      </div>
    )
  }

  return <PreferenceForm initialPreferences={initialPreferences} />
}
