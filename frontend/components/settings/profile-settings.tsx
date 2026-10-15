"use client"

import * as React from "react"
import { toast } from "sonner"
import { User, Save, AlertCircle } from "lucide-react"

import type { UserProfile } from "@/types/settings"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useProfile, useUpdateProfile } from "@/hooks/use-settings"
import { LoadingState } from "@/components/common/loading-state"
import { ErrorState } from "@/components/common/error-state"

const TIMEZONE_OPTIONS = [
  "UTC-08:00 (Pacific Time)",
  "UTC-07:00 (Mountain Time)",
  "UTC-06:00 (Central Time)",
  "UTC-05:00 (Eastern Time)",
  "UTC+00:00 (UTC)",
  "UTC+01:00 (Central European Time)",
  "UTC+05:30 (India Standard Time)",
  "UTC+08:00 (Singapore / China)",
  "UTC+09:00 (Japan Standard Time)",
]

interface ProfileFormProps {
  initialProfile: UserProfile
}

function ProfileForm({ initialProfile }: ProfileFormProps) {
  const updateMutation = useUpdateProfile()

  const [name, setName] = React.useState(initialProfile.name || "")
  const [email, setEmail] = React.useState(initialProfile.email || "")
  const [timezone, setTimezone] = React.useState(
    initialProfile.timezone || "UTC-05:00 (Eastern Time)"
  )
  const [errors, setErrors] = React.useState<{ name?: string; email?: string }>({})
  const [hasChanges, setHasChanges] = React.useState(false)

  const validate = () => {
    const newErrors: { name?: string; email?: string } = {}
    if (!name.trim()) {
      newErrors.name = "Full name is required."
    }
    if (!email.trim()) {
      newErrors.email = "Email address is required."
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      newErrors.email = "Please enter a valid email address."
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    try {
      await updateMutation.mutateAsync({
        name: name.trim(),
        email: email.trim().toLowerCase(),
        timezone,
      })
      setHasChanges(false)
      toast.success("Profile updated successfully", {
        description: "Your personal details have been saved.",
      })
    } catch {
      toast.error("Failed to update profile settings.")
    }
  }

  return (
    <form onSubmit={handleSave} className="flex flex-col gap-6">
      {/* Profile Card */}
      <div className="flex flex-col gap-5 rounded-lg border border-border bg-card p-5 shadow-2xs">
        <div className="flex items-start gap-3">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-md border border-border bg-muted/40 text-foreground">
            <User className="size-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-foreground">
              User Profile
            </h2>
            <p className="text-xs text-muted-foreground">
              Manage your display name, communication email, and regional timezone.
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 pt-2">
          {/* Full Name */}
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="profile-name"
              className="text-xs font-medium text-foreground"
            >
              Full Name
            </label>
            <div className="relative">
              <Input
                id="profile-name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value)
                  setHasChanges(true)
                  if (errors.name) setErrors((prev) => ({ ...prev, name: undefined }))
                }}
                placeholder="Your full name"
                className={errors.name ? "border-red-500" : ""}
                aria-invalid={!!errors.name}
                aria-describedby={errors.name ? "name-error" : undefined}
              />
            </div>
            {errors.name && (
              <span id="name-error" className="flex items-center gap-1 text-[11px] text-red-600 dark:text-red-400">
                <AlertCircle className="size-3" />
                {errors.name}
              </span>
            )}
          </div>

          {/* Email Address */}
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="profile-email"
              className="text-xs font-medium text-foreground"
            >
              Email Address
            </label>
            <div className="relative">
              <Input
                id="profile-email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  setHasChanges(true)
                  if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }))
                }}
                placeholder="your.email@example.com"
                className={errors.email ? "border-red-500" : ""}
                aria-invalid={!!errors.email}
                aria-describedby={errors.email ? "email-error" : undefined}
              />
            </div>
            {errors.email && (
              <span id="email-error" className="flex items-center gap-1 text-[11px] text-red-600 dark:text-red-400">
                <AlertCircle className="size-3" />
                {errors.email}
              </span>
            )}
          </div>

          {/* Timezone */}
          <div className="flex flex-col gap-1.5 sm:col-span-2">
            <label
              htmlFor="profile-timezone"
              className="text-xs font-medium text-foreground"
            >
              System Timezone
            </label>
            <Select
              value={timezone}
              onValueChange={(val) => {
                if (val) {
                  setTimezone(val)
                  setHasChanges(true)
                }
              }}
            >
              <SelectTrigger id="profile-timezone" className="w-full max-w-md">
                <SelectValue placeholder="Select timezone..." />
              </SelectTrigger>
              <SelectContent>
                {TIMEZONE_OPTIONS.map((tz) => (
                  <SelectItem key={tz} value={tz}>
                    {tz}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <span className="text-[11px] text-muted-foreground">
              All deadline computations and schedule timestamps will synchronize to this timezone.
            </span>
          </div>
        </div>
      </div>

      {/* Save Button Footer */}
      <div className="flex items-center justify-between border-t border-border/80 pt-4">
        {hasChanges ? (
          <span className="text-xs text-orange-600 dark:text-orange-400 font-medium">
            Unsaved profile changes
          </span>
        ) : (
          <span className="text-xs text-muted-foreground">
            Profile up to date
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
              <span>Save Profile</span>
            </>
          )}
        </Button>
      </div>
    </form>
  )
}

export function ProfileSettings() {
  const { data: initialProfile, isLoading, isError, refetch } = useProfile()

  if (isLoading) {
    return (
      <div className="rounded-lg border border-border bg-card p-8 shadow-2xs">
        <LoadingState message="Loading profile settings..." />
      </div>
    )
  }

  if (isError || !initialProfile) {
    return (
      <div className="rounded-lg border border-border bg-card p-6 shadow-2xs">
        <ErrorState
          title="Failed to load profile"
          message="Unable to retrieve profile information. Please check your connection."
          onRetry={() => refetch()}
        />
      </div>
    )
  }

  return <ProfileForm initialProfile={initialProfile} />
}
