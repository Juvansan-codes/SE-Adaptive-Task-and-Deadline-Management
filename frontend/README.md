# Adaptive Task & Deadline Management — Frontend

Frontend application for the **Adaptive Task & Deadline Management** system, built with Next.js (App Router), TypeScript, Tailwind CSS, and shadcn/ui.

---

## 🛠 Tech Stack

- **Framework:** [Next.js](https://nextjs.org/) (App Router)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **UI Library:** [shadcn/ui](https://ui.shadcn.com/)
- **Icons:** [Lucide React](https://lucide.dev/)
- **State Management & Fetching:** [TanStack Query](https://tanstack.com/query/latest)
- **Forms & Validation:** [React Hook Form](https://react-hook-form.com/) & [Zod](https://zod.dev/)
- **Date Utilities:** [date-fns](https://date-fns.org/)

---

## 📁 Project Structure

```
frontend/
├── app/                  # Next.js App Router (layout, providers, pages)
├── components/
│   ├── ui/               # shadcn/ui primitives (button, etc.)
│   ├── common/           # Shared cross-cutting components
│   ├── dashboard/        # Dashboard feature components
│   ├── tasks/            # Task management feature components
│   └── schedule/         # Scheduling feature components
├── hooks/                # Custom React hooks
├── services/
│   ├── api/              # API configuration and client modules
│   └── mock/             # Mock service definitions for prototyping
├── types/                # Global and domain TypeScript types
├── lib/                  # Shared helper functions and utility libraries
├── public/               # Static assets
└── docs/                 # Frontend technical documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js:** v18.18+ (tested on Node.js v24.x)
- **npm:** v9+ (or pnpm / yarn)

### 1. Installation

From the `frontend` directory:

```bash
npm install
```

### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env.local
```

Configure your backend API base URL in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

> **Note:** Public variables prefixed with `NEXT_PUBLIC_` are exposed in browser bundles. Do not include API secrets or credentials.

### 3. Running the Development Server

Start the development server with Turbopack:

```bash
npm run dev
```

The application will be accessible at [http://localhost:3000](http://localhost:3000).

### 4. Available Scripts

| Command | Description |
| :--- | :--- |
| `npm run dev` | Starts local Next.js development server |
| `npm run build` | Builds optimized production bundle |
| `npm run start` | Starts production server |
| `npm run lint` | Runs ESLint code quality checks |

---

## 🔒 Security Best Practices

- All browser-accessible configuration is scoped via `NEXT_PUBLIC_*`.
- `.env.local` and private credentials are excluded via `.gitignore`.
