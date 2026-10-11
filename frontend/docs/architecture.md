# Frontend Architecture

## Overview
This document outlines the directory structure, design system tokens, application shell architecture, authentication subsystem, and task management subsystem for the **Adaptive Task & Deadline Management** frontend.

---

## Technology Stack
- **Framework:** Next.js (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **UI Components:** shadcn/ui
- **Icons:** Lucide React
- **Toast Engine:** Sonner (`sonner` + `next-themes`)
- **Server State & Data Fetching:** TanStack Query (`@tanstack/react-query`)
- **Form Management:** React Hook Form (`react-hook-form` + `@hookform/resolvers`)
- **Schema Validation:** Zod (`zod`)
- **Date Utilities:** date-fns (`date-fns`)

---

## Design System (Phase 1)

### Visual Direction & Color Palette
Minimalist, editorial, productivity-focused interface avoiding gradients, neon colors, and excessive shadows:
- **White:** `#FFFFFF` — Primary surfaces and card backgrounds (`--background`, `--card`, `--popover`)
- **Near-black:** `#171717` — Text and dark branding accents (`--foreground`, `--sidebar-foreground`)
- **Light gray:** `#F5F5F5` — Secondary surfaces, hover states (`--secondary`, `--muted`, `--sidebar-accent`)
- **Border gray:** `#E5E5E5` — Restrained borders and dividers (`--border`, `--input`, `--sidebar-border`)
- **Secondary text:** `#737373` — Muted labels and subtitles (`--muted-foreground`)
- **Orange accent:** `#F97316` — Primary actions, active indicators, focus rings, recommendations (`--primary`, `--ring`)

### Typography & Spacing
- **Font Stack:** Geist Sans and Geist Mono
- **Border Radius:** Restrained 6px (`--radius: 0.375rem`)
- **Control Heights:** Standardized 36px (`h-9`) for inputs, buttons, and select triggers
- **Focus Rings:** High-visibility 2px orange ring with offset (`focus-visible:ring-2 focus-visible:ring-ring/40 focus-visible:ring-offset-1`)
- **Reduced Motion:** Global CSS media query clamps animation durations when `prefers-reduced-motion` is enabled

---

## Reusable UI Component Library

### Atomic UI Components (`components/ui/`)
- `Button`: Primary (`#F97316`), Secondary, Outline, Destructive, Ghost, and Link variants
- `Input`: Text inputs with consistent `h-9` control height and restrained borders
- `Select`: Accessible dropdown selection using Base UI primitives
- `Badge`: Restrained badges in Default (orange), Secondary, Outline, Destructive, and Accent
- `Dialog`: Accessible modal dialogs with keyboard trap and backdrop
- `DropdownMenu`: Accessible context action menus
- `Progress`: Clean progress indicator with orange accent bar
- `Toaster` / `Sonner`: Toast notification provider

### Common State & Shell Components (`components/common/`)
- `AppShell`: Persistent desktop sidebar, top bar, and mobile navigation drawer
- `EmptyState`: Clean empty state presentation with icon, title, description, and action slots
- `LoadingState`: Accessible loading indicator with reduced-motion support
- `ErrorState`: Alert box with retry trigger and error messaging

### Task Domain Components (`components/tasks/`)
- `TaskCard`: Grid card view with progress bars, status badges, and quick actions
- `TaskRow`: Dense row view for compact lists
- `TaskList`: Complete task management container with search, multi-faceted filtering, sorting, view toggling, and delete confirmation dialog
- `TaskForm`: Modal dialog form for creating and editing tasks with Zod validation
- `TaskDetails`: Deep-dive inspector for `/tasks/[id]` with metadata, audit trail, and duration metrics
- `PriorityBadge`: Semantic badge for critical, high, medium, and low priority
- `DifficultyBadge`: Complexity indicator (easy, medium, hard)
- `StatusBadge`: Semantic badge for pending, in_progress, completed, and overdue
- `ProgressBar`: Progress visualization with duration indicators (`Xh / Yh`)
- `DeadlineIndicator`: Date-fns powered deadline formatting with relative distance and overdue warning

---

## Task Management Subsystem (Phase 3)

### Task Model (`types/task.ts`)
```ts
interface Task {
  id: string
  title: string
  description: string
  category: string
  deadline: string
  priority: "low" | "medium" | "high" | "critical"
  difficulty: "easy" | "medium" | "hard"
  estimatedDuration: number
  completedDuration: number
  remainingDuration: number
  progress: number
  status: "pending" | "in_progress" | "completed" | "overdue"
  createdAt: string
  updatedAt: string
}
```

### Mock Service (`services/mock/tasks.ts`)
- **In-Memory Store:** Shared `mockTasksStore` maintaining state across client navigations.
- **Service API:**
  - `getTasks(filter)`: Multi-criteria filtering by text, category, priority, status, and sorting.
  - `getTask(id)`: Single task retrieval with not-found handling.
  - `createTask(data)`: Appends task with auto-computed remaining duration and progress percentage.
  - `updateTask(id, updates)`: Updates task and recalculates progress/status.
  - `deleteTask(id)`: Removes task from storage.
  - `getCategories()`: Returns distinct categories for dynamic filter pills.
- **TanStack Query Hooks (`hooks/use-tasks.ts`):** Reactive query and mutation bindings with automatic cache invalidation on mutations.

---

## Core Routes
- `/`: Automatically redirects to `/dashboard`
- `/dashboard`: High-level overview placeholder
- `/tasks`: Comprehensive task list and task management interface
- `/tasks/[id]`: Dynamic task details route with edit, status, and delete controls
- `/schedule`: Adaptive scheduling and timeline forecasting placeholder
- `/settings`: Preference configuration and component showcase
- `/login`: Standalone focused authentication page
- `/register`: Standalone focused registration page

---

## Folder Structure
```
frontend/
├── app/
│   ├── dashboard/page.tsx        # Dashboard route
│   ├── tasks/
│   │   ├── page.tsx              # Tasks list route
│   │   └── [id]/page.tsx         # Dynamic task detail route
│   ├── schedule/page.tsx         # Schedule route
│   ├── settings/page.tsx         # Settings & component showcase route
│   ├── login/page.tsx            # Login authentication route
│   ├── register/page.tsx         # Registration authentication route
│   ├── globals.css               # Design tokens, theme variables, and reset
│   ├── layout.tsx                # Root layout wrapping AppShell & Providers
│   ├── page.tsx                  # Root route redirect
│   └── providers.tsx             # TanStack Query & Sonner providers
├── components/
│   ├── auth/                     # Reusable auth components
│   ├── common/                   # Shared shell and state components
│   ├── tasks/                    # Task management components
│   └── ui/                       # Reusable atomic UI components (shadcn/ui)
├── docs/
│   └── architecture.md           # Technical architecture specification
├── hooks/
│   └── use-tasks.ts              # TanStack Query hooks for task entities
├── lib/
│   ├── validations/
│   │   ├── auth.ts               # Auth Zod schemas
│   │   └── task.ts               # Task Zod validation schemas
│   └── utils.ts                  # Class merging utilities
├── services/
│   ├── api/                      # Future API client configuration
│   └── mock/
│       ├── auth.ts               # Mock authentication service
│       └── tasks.ts              # Mock task management service
└── types/
    ├── auth.ts                   # Authentication domain types
    ├── task.ts                   # Task domain models & filter interfaces
    └── index.ts                  # Global type exports
```
