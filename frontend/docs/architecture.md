# Frontend Architecture - Phase 0 Foundation

## Overview
This document outlines the directory structure, technology stack, and foundational design principles for the **Adaptive Task & Deadline Management** frontend.

## Technology Stack
- **Framework:** Next.js (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **UI Components:** shadcn/ui
- **Icons:** Lucide React
- **Server State & Data Fetching:** TanStack Query (`@tanstack/react-query`)
- **Form Management:** React Hook Form (`react-hook-form` + `@hookform/resolvers`)
- **Schema Validation:** Zod (`zod`)
- **Date Utilities:** date-fns (`date-fns`)

## Folder Structure
```
frontend/
├── app/                  # Next.js App Router pages, layout, and client providers
├── components/
│   ├── ui/               # shadcn/ui base atomic primitives (buttons, inputs, dialogs, etc.)
│   ├── common/           # Shared reusable components (headers, navbars, modals, loaders)
│   ├── dashboard/        # Dashboard-specific UI modules (Phase 1+)
│   ├── tasks/            # Task management UI modules (Phase 1+)
│   └── schedule/         # Schedule and calendar UI modules (Phase 1+)
├── hooks/                # Custom React hooks
├── services/
│   ├── api/              # API client and HTTP services
│   └── mock/             # Mock data and test handlers
├── types/                # TypeScript interface and type declarations
├── lib/                  # Utility helpers and library wrappers (e.g., utils.ts for cn)
├── public/               # Static assets (images, icons, fonts)
└── docs/                 # Project frontend documentation
```

## Environment Configuration
The frontend communicates with backend services configured through environment variables:
- `NEXT_PUBLIC_API_URL`: Base URL for the backend API endpoints (configured in `.env.example` and `.env.local`).
- Browser-accessible environment variables are prefixed with `NEXT_PUBLIC_`.
- Public environment variables must **never** contain sensitive secrets or tokens.
