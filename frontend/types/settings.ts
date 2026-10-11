export type DayOfWeek =
  | "monday"
  | "tuesday"
  | "wednesday"
  | "thursday"
  | "friday"
  | "saturday"
  | "sunday"

export interface DayAvailability {
  day: DayOfWeek
  label: string
  enabled: boolean
  startTime: string // "HH:mm" e.g. "09:00"
  endTime: string   // "HH:mm" e.g. "17:00"
}

export type WeeklyAvailability = DayAvailability[]

export interface UserProfile {
  id: string
  name: string
  email: string
  timezone: string
  role?: string
}

export interface UserPreferences {
  enableDeadlineReminders: boolean
  enableScheduleUpdates: boolean
  defaultTaskDurationMinutes: number
  dailyFocusHoursLimit: number
  bufferStrategy: "tight" | "moderate" | "relaxed"
}

export interface SettingsState {
  profile: UserProfile
  preferences: UserPreferences
  availability: WeeklyAvailability
}
