"use client"

import * as React from "react"
import { toast } from "sonner"
import {
  Bell,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Info,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { LoadingState } from "@/components/common/loading-state"
import { ErrorState } from "@/components/common/error-state"

export default function SettingsPage() {
  const [dialogOpen, setDialogOpen] = React.useState(false)
  const [activeTab, setActiveTab] = React.useState<"general" | "components">("general")

  const handleTestToast = (type: "success" | "info" | "warning") => {
    switch (type) {
      case "success":
        toast.success("Schedule settings saved successfully.")
        break
      case "info":
        toast.info("Adaptive rescheduling is set to automatic.")
        break
      case "warning":
        toast.warning("Task buffer threshold is low (10%).")
        break
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex flex-col gap-1.5 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground md:text-2xl">
            Settings
          </h1>
          <p className="text-sm text-muted-foreground">
            Configure scheduling preferences, notification thresholds, and working hours.
          </p>
        </div>
        <div className="flex items-center gap-2 pt-2 md:pt-0">
          <Badge variant="outline" className="text-xs">
            Presentational
          </Badge>
          <Button
            variant="primary"
            size="sm"
            onClick={() => handleTestToast("success")}
          >
            Save Changes
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-border pb-px">
        <button
          type="button"
          onClick={() => setActiveTab("general")}
          className={`px-3 py-1.5 text-xs font-medium border-b-2 transition-colors cursor-pointer ${
            activeTab === "general"
              ? "border-primary text-foreground font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          General Preferences
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("components")}
          className={`px-3 py-1.5 text-xs font-medium border-b-2 transition-colors cursor-pointer ${
            activeTab === "components"
              ? "border-primary text-foreground font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          UI Component Showcase
        </button>
      </div>

      {activeTab === "general" ? (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Working Hours Card */}
          <div className="flex flex-col gap-4 rounded-lg border border-border bg-card p-5 shadow-2xs">
            <div className="flex items-center gap-2">
              <Sliders className="size-4 text-primary" />
              <h2 className="text-sm font-semibold tracking-tight text-foreground">
                Workload Parameters
              </h2>
            </div>
            <p className="text-xs text-muted-foreground">
              Define daily working capacity and default estimation buffers.
            </p>

            <div className="space-y-3 pt-1">
              <div className="space-y-1.5">
                <label htmlFor="daily-hours" className="text-xs font-medium text-foreground">
                  Daily Working Hours
                </label>
                <Input
                  id="daily-hours"
                  defaultValue="6.5"
                  placeholder="e.g. 6.0"
                  className="max-w-xs"
                />
              </div>

              <div className="space-y-1.5">
                <label htmlFor="buffer-strategy" className="text-xs font-medium text-foreground">
                  Deadline Buffer Strategy
                </label>
                <Select defaultValue="moderate">
                  <SelectTrigger id="buffer-strategy" className="w-full max-w-xs">
                    <SelectValue placeholder="Select buffer..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tight">Strict (10% Buffer)</SelectItem>
                    <SelectItem value="moderate">Moderate (20% Buffer)</SelectItem>
                    <SelectItem value="relaxed">Conservative (35% Buffer)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1.5 pt-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-foreground">Buffer Calibration</span>
                  <span className="text-muted-foreground">20% allocated</span>
                </div>
                <Progress value={20} className="w-full" />
              </div>
            </div>
          </div>

          {/* Notifications Card */}
          <div className="flex flex-col gap-4 rounded-lg border border-border bg-card p-5 shadow-2xs">
            <div className="flex items-center gap-2">
              <Bell className="size-4 text-primary" />
              <h2 className="text-sm font-semibold tracking-tight text-foreground">
                System Alerts
              </h2>
            </div>
            <p className="text-xs text-muted-foreground">
              Test notification triggers and toast messages.
            </p>

            <div className="flex flex-col gap-2.5 pt-1">
              <div className="flex items-center justify-between rounded-md border border-border/60 bg-secondary/30 p-2.5">
                <div className="flex flex-col">
                  <span className="text-xs font-medium text-foreground">Success Notification</span>
                  <span className="text-[11px] text-muted-foreground">Trigger confirmation toast</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleTestToast("success")}
                >
                  <CheckCircle2 className="size-3.5 text-emerald-600" />
                  <span>Test</span>
                </Button>
              </div>

              <div className="flex items-center justify-between rounded-md border border-border/60 bg-secondary/30 p-2.5">
                <div className="flex flex-col">
                  <span className="text-xs font-medium text-foreground">System Advisory</span>
                  <span className="text-[11px] text-muted-foreground">Trigger informational toast</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleTestToast("info")}
                >
                  <Info className="size-3.5 text-sky-600" />
                  <span>Test</span>
                </Button>
              </div>

              <div className="flex items-center justify-between rounded-md border border-border/60 bg-secondary/30 p-2.5">
                <div className="flex flex-col">
                  <span className="text-xs font-medium text-foreground">Deadline Warning</span>
                  <span className="text-[11px] text-muted-foreground">Trigger warning toast</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleTestToast("warning")}
                >
                  <AlertTriangle className="size-3.5 text-primary" />
                  <span>Test</span>
                </Button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* UI Components Showcase */
        <div className="flex flex-col gap-6">
          {/* Buttons & Badges */}
          <div className="flex flex-col gap-4 rounded-lg border border-border bg-card p-5 shadow-2xs">
            <h2 className="text-sm font-semibold tracking-tight text-foreground">
              Buttons &amp; Badges
            </h2>
            <div className="flex flex-wrap items-center gap-2.5">
              <Button variant="primary">Primary Action</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="primary" size="sm">Small Primary</Button>
              <Button variant="outline" disabled>Disabled</Button>
            </div>
            <div className="flex flex-wrap items-center gap-2 pt-2">
              <Badge variant="default">Primary Badge</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="outline">Outline</Badge>
              <Badge variant="destructive">Destructive</Badge>
              <Badge variant="accent">Accent</Badge>
            </div>
          </div>

          {/* Dialog & Dropdown Menu */}
          <div className="flex flex-col gap-4 rounded-lg border border-border bg-card p-5 shadow-2xs">
            <h2 className="text-sm font-semibold tracking-tight text-foreground">
              Modals &amp; Dropdowns
            </h2>
            <div className="flex flex-wrap items-center gap-3">
              {/* Dialog Preview */}
              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger render={<Button variant="outline" size="sm" />}>
                  Open Dialog Preview
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Confirm Schedule Calibration</DialogTitle>
                    <DialogDescription>
                      This dialog demonstrates accessible modal interaction with keyboard trap and focus return.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="py-2 text-xs text-muted-foreground">
                    Phase 1 design system modal dialog.
                  </div>
                  <DialogFooter>
                    <DialogClose render={<Button variant="outline" size="sm" />}>
                      Cancel
                    </DialogClose>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        setDialogOpen(false)
                        toast.success("Dialog confirmed.")
                      }}
                    >
                      Confirm
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>

              {/* Dropdown Menu Preview */}
              <DropdownMenu>
                <DropdownMenuTrigger render={<Button variant="outline" size="sm" />}>
                  Action Menu
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  <DropdownMenuLabel>Quick Options</DropdownMenuLabel>
                  <DropdownMenuItem onClick={() => toast.info("Option 1 chosen")}>
                    Inspect Tasks
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => toast.info("Option 2 chosen")}>
                    Calibrate Engine
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => toast.info("Archived")}>
                    Archive View
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          {/* States: Loading & Error */}
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-lg border border-border bg-card p-4 shadow-2xs">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Loading State Component
              </h3>
              <LoadingState
                message="Calculating adaptive buffers..."
                description="Simulated loading state demonstration"
                size="default"
              />
            </div>
            <div className="rounded-lg border border-border bg-card p-4 shadow-2xs">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Error State Component
              </h3>
              <ErrorState
                title="Scheduling conflict detected"
                message="Two high-priority deadlines overlap during constrained working hours."
                onRetry={() => toast.info("Simulated retry initiated")}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
