"use client"

import * as React from "react"
import { toast } from "sonner"
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Flame,
  Layers,
  RotateCcw,
  ShieldAlert,
  Sparkles,
  Zap,
} from "lucide-react"

import type {
  DisruptionType,
  DisruptionSimulationResult,
  RecoveryStrategy,
} from "@/types"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { PriorityBadge } from "@/components/tasks/priority-badge"
import {
  useSimulateDisruption,
  useApplyRecoveryStrategy,
} from "@/hooks/use-schedule"
import { useTasks } from "@/hooks/use-tasks"

interface DisruptionSimulatorDialogProps {
  currentDate?: string
  trigger?: React.ReactNode
}

export function DisruptionSimulatorDialog({
  currentDate,
  trigger,
}: DisruptionSimulatorDialogProps) {
  const [open, setOpen] = React.useState(false)
  const [disruptionType, setDisruptionType] =
    React.useState<DisruptionType>("lost_time")
  const [hoursLost, setHoursLost] = React.useState<number>(2.5)
  const [overrunTaskId, setOverrunTaskId] = React.useState<string>("")
  const [additionalHours, setAdditionalHours] = React.useState<number>(3.0)

  const [simulationResult, setSimulationResult] =
    React.useState<DisruptionSimulationResult | null>(null)

  const { data: tasksData } = useTasks()
  const activeTasks = React.useMemo(() => {
    return (tasksData || []).filter(
      (t) => t.status !== "completed" && t.remainingDuration > 0
    )
  }, [tasksData])

  // Select first active task as default overrun candidate
  React.useEffect(() => {
    if (!overrunTaskId && activeTasks.length > 0) {
      setOverrunTaskId(activeTasks[0].id)
    }
  }, [activeTasks, overrunTaskId])

  const simulateMutation = useSimulateDisruption()
  const applyMutation = useApplyRecoveryStrategy()

  const handleRunSimulation = () => {
    setSimulationResult(null)
    simulateMutation.mutate(
      {
        disruptionType,
        targetDate: currentDate,
        hoursLost: disruptionType === "lost_time" ? Number(hoursLost) : 0,
        overrunTaskId: disruptionType === "task_overrun" ? overrunTaskId : undefined,
        additionalHours:
          disruptionType === "task_overrun" ? Number(additionalHours) : 0,
      },
      {
        onSuccess: (result) => {
          setSimulationResult(result)
          if (result.breachedTasksCount === 0) {
            toast.info("Resilient Schedule", {
              description:
                "Existing buffers are sufficient to absorb this disruption.",
            })
          } else {
            toast.warning("Cascading Breaches Detected", {
              description: `${result.breachedTasksCount} deadline(s) compromised. 3 recovery strategies ready.`,
            })
          }
        },
        onError: () => {
          toast.error("Simulation Failed", {
            description: "Unable to run what-if cascade simulation.",
          })
        },
      }
    )
  }

  const handleApplyStrategy = (strategy: RecoveryStrategy) => {
    applyMutation.mutate(
      {
        strategyId: strategy.id,
        strategyType: strategy.strategyType,
        actionPayload: strategy.actionPayload,
        targetDate: currentDate,
      },
      {
        onSuccess: (res) => {
          toast.success("Recovery Strategy Applied!", {
            description: res.changesApplied[0] || res.message,
          })
          setOpen(false)
          setSimulationResult(null)
        },
        onError: () => {
          toast.error("Failed to Apply Strategy", {
            description: "Could not commit recovery adjustments to schedule.",
          })
        },
      }
    )
  }

  const handleResetSimulation = () => {
    setSimulationResult(null)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<div>{trigger}</div>} />
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto p-6 gap-6">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <span className="flex size-7 items-center justify-center rounded-[6px] bg-primary/10 text-primary">
              <Zap className="size-4" />
            </span>
            <DialogTitle className="text-lg font-semibold tracking-[-0.02em]">
              What-If Disruption Simulator
            </DialogTitle>
            <Badge variant="outline" className="text-[11px] font-mono ml-auto">
              SANDBOX
            </Badge>
          </div>
          <DialogDescription className="text-xs text-muted-foreground">
            Simulate the cascading ripple effect of schedule disruptions across
            the next 7 days and evaluate automated recovery plans with zero risk
            to live data.
          </DialogDescription>
        </DialogHeader>

        {/* INPUT FORM: Disruption Parameters */}
        <div className="flex flex-col gap-4 rounded-[8px] border border-border bg-muted/30 p-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-foreground">
              Disruption Scenario
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  setDisruptionType("lost_time")
                  setSimulationResult(null)
                }}
                className={`flex items-center gap-2 rounded-[6px] border px-3 py-2 text-left text-xs font-medium transition-colors ${
                  disruptionType === "lost_time"
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border bg-card text-muted-foreground hover:bg-muted"
                }`}
              >
                <Clock className="size-4 shrink-0" />
                <div>
                  <div>Lost Focus Capacity</div>
                  <div className="text-[10px] font-normal opacity-80">
                    Emergency, meeting, illness
                  </div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setDisruptionType("task_overrun")
                  setSimulationResult(null)
                }}
                className={`flex items-center gap-2 rounded-[6px] border px-3 py-2 text-left text-xs font-medium transition-colors ${
                  disruptionType === "task_overrun"
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border bg-card text-muted-foreground hover:bg-muted"
                }`}
              >
                <AlertTriangle className="size-4 shrink-0" />
                <div>
                  <div>Task Duration Overrun</div>
                  <div className="text-[10px] font-normal opacity-80">
                    Scope expansion, blocker
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Conditional Input Controls */}
          {disruptionType === "lost_time" ? (
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-medium text-foreground">
                  Hours Lost Today
                </label>
                <span className="font-mono text-xs font-semibold text-primary tabular-nums">
                  {hoursLost}h lost
                </span>
              </div>
              <div className="flex items-center gap-2">
                {[1.0, 2.0, 3.0, 4.0].map((h) => (
                  <button
                    key={h}
                    type="button"
                    onClick={() => setHoursLost(h)}
                    className={`flex-1 rounded-[6px] border py-1 text-xs font-mono transition-colors ${
                      hoursLost === h
                        ? "border-primary bg-primary text-primary-foreground font-semibold"
                        : "border-border bg-card hover:bg-muted text-muted-foreground"
                    }`}
                  >
                    {h}h
                  </button>
                ))}
                <Input
                  type="number"
                  step="0.5"
                  min="0.5"
                  max="12"
                  value={hoursLost}
                  onChange={(e) => setHoursLost(Number(e.target.value))}
                  className="w-20 font-mono text-xs text-center"
                />
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-foreground">
                  Stalled / Overrunning Task
                </label>
                <select
                  value={overrunTaskId}
                  onChange={(e) => setOverrunTaskId(e.target.value)}
                  className="h-9 w-full rounded-[6px] border border-input bg-card px-3 text-xs text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                >
                  {activeTasks.map((t) => (
                    <option key={t.id} value={t.id}>
                      [{t.priority.toUpperCase()}] {t.title} ({t.remainingDuration}h rem)
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-foreground">
                    Additional Hours Required
                  </label>
                  <span className="font-mono text-xs font-semibold text-primary tabular-nums">
                    +{additionalHours}h overrun
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {[1.5, 2.5, 3.5, 5.0].map((h) => (
                    <button
                      key={h}
                      type="button"
                      onClick={() => setAdditionalHours(h)}
                      className={`flex-1 rounded-[6px] border py-1 text-xs font-mono transition-colors ${
                        additionalHours === h
                          ? "border-primary bg-primary text-primary-foreground font-semibold"
                          : "border-border bg-card hover:bg-muted text-muted-foreground"
                      }`}
                    >
                      +{h}h
                    </button>
                  ))}
                  <Input
                    type="number"
                    step="0.5"
                    min="0.5"
                    max="20"
                    value={additionalHours}
                    onChange={(e) => setAdditionalHours(Number(e.target.value))}
                    className="w-20 font-mono text-xs text-center"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Run Action */}
          <div className="flex items-center justify-between pt-1">
            <span className="text-[11px] text-muted-foreground">
              Simulation horizon: 7 calendar days
            </span>
            <div className="flex items-center gap-2">
              {simulationResult && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleResetSimulation}
                  className="h-8 text-xs text-muted-foreground"
                >
                  <RotateCcw className="size-3 mr-1" />
                  Reset
                </Button>
              )}
              <Button
                variant="default"
                size="sm"
                onClick={handleRunSimulation}
                disabled={simulateMutation.isPending}
                className="h-8 text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {simulateMutation.isPending ? (
                  "Simulating Cascade..."
                ) : (
                  <>
                    <Activity className="size-3.5 mr-1.5" />
                    Run Impact Simulation
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* SIMULATION RESULTS VIEW */}
        {simulationResult && (
          <div className="flex flex-col gap-5 pt-1 animate-in fade-in-50 duration-200">
            {/* Feasibility Comparison Scoreboard */}
            <div className="rounded-[8px] border border-border bg-card p-4 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold tracking-wide uppercase text-muted-foreground">
                  Cascading Impact Scorecard
                </span>
                <span className="text-xs text-muted-foreground font-mono">
                  Horizon: {simulationResult.targetDate} +7d
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="rounded-[6px] border border-border bg-muted/20 p-2.5">
                  <div className="text-[11px] text-muted-foreground">Baseline</div>
                  <div className="text-lg font-bold font-mono text-foreground">
                    {simulationResult.baselineFeasibilityPct}%
                  </div>
                  <div className="text-[10px] text-muted-foreground">On-Time</div>
                </div>

                <div className="rounded-[6px] border border-border bg-muted/20 p-2.5">
                  <div className="text-[11px] text-muted-foreground">Disrupted</div>
                  <div
                    className={`text-lg font-bold font-mono ${
                      simulationResult.disruptedFeasibilityPct < 80
                        ? "text-destructive"
                        : "text-foreground"
                    }`}
                  >
                    {simulationResult.disruptedFeasibilityPct}%
                  </div>
                  <div className="text-[10px] text-muted-foreground">On-Time</div>
                </div>

                <div className="rounded-[6px] border border-border bg-muted/20 p-2.5">
                  <div className="text-[11px] text-muted-foreground">
                    Breached Deadlines
                  </div>
                  <div
                    className={`text-lg font-bold font-mono ${
                      simulationResult.breachedTasksCount > 0
                        ? "text-destructive"
                        : "text-emerald-600"
                    }`}
                  >
                    {simulationResult.breachedTasksCount}
                  </div>
                  <div className="text-[10px] text-muted-foreground">
                    {simulationResult.breachedTasksCount === 0
                      ? "Zero Impact"
                      : "Delayed Downstream"}
                  </div>
                </div>
              </div>

              {/* Breached Tasks Roster */}
              {simulationResult.breachedTasks.length > 0 && (
                <div className="mt-3.5 flex flex-col gap-2 pt-3 border-t border-border">
                  <div className="text-[11px] font-medium text-destructive flex items-center gap-1.5">
                    <ShieldAlert className="size-3.5" />
                    Tasks Breaching Deadline Downstream:
                  </div>
                  <div className="flex flex-col gap-1.5">
                    {simulationResult.breachedTasks.map((bt) => (
                      <div
                        key={bt.taskId}
                        className="flex items-center justify-between rounded-[6px] border border-destructive/20 bg-destructive/5 px-2.5 py-1.5 text-xs"
                      >
                        <div className="flex items-center gap-2 overflow-hidden mr-2">
                          <PriorityBadge priority={bt.priority} />
                          <span className="font-medium text-foreground truncate">
                            {bt.title}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 shrink-0 font-mono text-[11px]">
                          <span className="text-muted-foreground">
                            +{bt.delayHours}h delay
                          </span>
                          <span className="font-semibold text-destructive">
                            +{bt.breachMagnitudeHours}h breach
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Candidate Recovery Strategies */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="size-4 text-primary" />
                  <h3 className="text-sm font-semibold text-foreground">
                    Synthesized Recovery Strategies
                  </h3>
                </div>
                <span className="text-[11px] text-muted-foreground">
                  Select a plan to adapt schedule
                </span>
              </div>

              <div className="flex flex-col gap-3">
                {simulationResult.strategies.map((strat) => (
                  <div
                    key={strat.id}
                    className={`relative rounded-[8px] border p-4 transition-all ${
                      strat.isRecommended
                        ? "border-primary/50 bg-primary/[0.02] shadow-[0_2px_8px_rgba(249,115,22,0.06)]"
                        : "border-border bg-card"
                    }`}
                  >
                    {strat.isRecommended && (
                      <div className="absolute -top-2.5 right-3">
                        <Badge className="bg-primary text-primary-foreground text-[10px] font-medium px-2 py-0.5 shadow-xs">
                          RECOMMENDED
                        </Badge>
                      </div>
                    )}

                    <div className="flex flex-col gap-3">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-sm text-foreground">
                              {strat.title}
                            </span>
                            <Badge
                              variant="outline"
                              className="text-[10px] font-normal"
                            >
                              {strat.badge}
                            </Badge>
                          </div>
                          <p className="mt-1 text-xs text-muted-foreground">
                            {strat.description}
                          </p>
                        </div>

                        {/* Feasibility Metric Capsule */}
                        <div className="text-right shrink-0">
                          <div className="font-mono text-sm font-bold text-foreground">
                            {strat.feasibilityScore}%
                          </div>
                          <div className="text-[10px] text-muted-foreground">
                            Feasibility
                          </div>
                        </div>
                      </div>

                      {/* Changes Checklist */}
                      <ul className="flex flex-col gap-1 text-[11px] text-muted-foreground bg-muted/30 rounded-[6px] p-2.5">
                        {strat.changesSummary.map((ch, idx) => (
                          <li key={idx} className="flex items-start gap-1.5">
                            <CheckCircle2 className="size-3 text-primary shrink-0 mt-0.5" />
                            <span>{ch}</span>
                          </li>
                        ))}
                      </ul>

                      {/* Footer Actions */}
                      <div className="flex items-center justify-between pt-1">
                        <div className="flex items-center gap-2">
                          <span className="text-[11px] text-muted-foreground">
                            Stress Index:
                          </span>
                          <span
                            className={`text-[11px] font-medium capitalize ${
                              strat.stressIndex === "low"
                                ? "text-emerald-600 font-semibold"
                                : strat.stressIndex === "moderate"
                                ? "text-amber-600 font-semibold"
                                : "text-destructive font-semibold"
                            }`}
                          >
                            {strat.stressIndex}
                          </span>
                          {strat.deadlinesSavedCount > 0 && (
                            <span className="text-[11px] text-muted-foreground">
                              • Saves {strat.deadlinesSavedCount} deadline(s)
                            </span>
                          )}
                        </div>

                        <Button
                          variant={strat.isRecommended ? "default" : "outline"}
                          size="sm"
                          disabled={applyMutation.isPending}
                          onClick={() => handleApplyStrategy(strat)}
                          className={`h-8 text-xs font-medium ${
                            strat.isRecommended
                              ? "bg-primary text-primary-foreground hover:bg-primary/90"
                              : ""
                          }`}
                        >
                          {applyMutation.isPending ? (
                            "Applying..."
                          ) : (
                            <>
                              Apply Strategy
                              <ArrowRight className="size-3 ml-1" />
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

