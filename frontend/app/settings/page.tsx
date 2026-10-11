"use client"

import * as React from "react"
import { Calendar, User, Sliders } from "lucide-react"

import {
  AvailabilityEditor,
  ProfileSettings,
  PreferenceSettings,
} from "@/components/settings"
import { cn } from "@/lib/utils"

type SettingsTab = "availability" | "profile" | "preferences"

export default function SettingsPage() {
  const [activeTab, setActiveTab] = React.useState<SettingsTab>("availability")

  const tabs = [
    {
      id: "availability" as SettingsTab,
      label: "Availability",
      icon: Calendar,
      description: "Weekly focus hours and work schedule",
    },
    {
      id: "profile" as SettingsTab,
      label: "Profile",
      icon: User,
      description: "Personal details and timezone",
    },
    {
      id: "preferences" as SettingsTab,
      label: "Preferences",
      icon: Sliders,
      description: "Notifications and buffer strategy",
    },
  ]

  return (
    <div className="flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex flex-col gap-1.5 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground md:text-2xl">
            Settings &amp; Availability
          </h1>
          <p className="text-sm text-muted-foreground">
            Configure your active study capacity, notification thresholds, and personal parameters.
          </p>
        </div>
      </div>

      {/* Settings Navigation Tabs */}
      <div className="flex items-center gap-1 border-b border-border/80 pb-px overflow-x-auto scrollbar-none">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "inline-flex items-center gap-2 border-b-2 px-3.5 py-2 text-xs font-medium transition-colors cursor-pointer whitespace-nowrap",
                isActive
                  ? "border-primary text-foreground font-semibold"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              )}
            >
              <Icon
                className={cn(
                  "size-3.5",
                  isActive ? "text-primary" : "text-muted-foreground"
                )}
              />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Main Tab Content */}
      <div className="max-w-4xl">
        {activeTab === "availability" && <AvailabilityEditor />}
        {activeTab === "profile" && <ProfileSettings />}
        {activeTab === "preferences" && <PreferenceSettings />}
      </div>
    </div>
  )
}
