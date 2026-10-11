# Frontend Architecture

## Overview
This document outlines the directory structure, design system tokens, and application shell architecture for the **Adaptive Task & Deadline Management** frontend.

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

---

## Application Shell & Routing

### Shell Layout
- **Desktop Sidebar:** Fixed 256px (`w-64`) left sidebar with brand logo, main navigation, and status badge.
- **Top Bar:** Sticky header with current route title, breadcrumb, and mobile menu trigger.
- **Mobile Navigation:** Slide-out drawer with backdrop blur, touch-friendly targets (`min-h-[44px]`), and escape key listener.

### Core Routes
- `/`: Automatically redirects to `/dashboard`
- `/dashboard`: High-level overview placeholder
- `/tasks`: Workload and task management placeholder
- `/schedule`: Adaptive scheduling and timeline forecasting placeholder
- `/settings`: Preference configuration and component showcase

---

## Folder Structure
```
frontend/
├── app/
│   ├── dashboard/page.tsx    # Dashboard route
│   ├── tasks/page.tsx        # Tasks route
│   ├── schedule/page.tsx     # Schedule route
│   ├── settings/page.tsx     # Settings & component showcase route
│   ├── globals.css           # Design tokens, theme variables, and reset
│   ├── layout.tsx            # Root layout wrapping AppShell & Providers
│   ├── page.tsx              # Root route redirect
│   └── providers.tsx         # TanStack Query & Sonner providers
├── components/
│   ├── common/
│   │   ├── app-shell.tsx     # Desktop sidebar, mobile drawer, topbar
│   │   ├── empty-state.tsx   # Reusable empty state component
│   │   ├── loading-state.tsx # Accessible loading state component
│   │   ├── error-state.tsx   # Accessible error state component
│   │   └── index.ts          # Common barrel export
│   └── ui/                   # Reusable atomic UI components (shadcn/ui)
├── docs/
│   └── architecture.md       # Technical architecture specification
├── lib/
│   └── utils.ts              # Class merging utilities
├── public/                   # Static assets
└── services/                 # API configuration and clients
```
