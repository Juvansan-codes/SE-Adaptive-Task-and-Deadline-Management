# Adaptive Task & Deadline Management — Backend API

FastAPI backend foundation for the **Adaptive Task & Deadline Management** web application. Built with Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic, and Pydantic Settings.

---

## 🛠 Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (0.115+)
- **ASGI Server:** [Uvicorn](https://www.uvicorn.org/)
- **ORM:** [SQLAlchemy 2.x](https://www.sqlalchemy.org/) (Synchronous engine with `pool_pre_ping`)
- **Database Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Configuration & Validation:** [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- **Database Driver:** [psycopg (v3)](https://www.psycopg.org/psycopg3/)
- **Database Engine:** PostgreSQL (Hosted on [Supabase](https://supabase.com/))
- **Testing:** [pytest](https://docs.pytest.org/) & [HTTPX](https://www.python-httpx.org/) / `TestClient`

---

## 📁 Backend Structure

```
backend/
├── app/
│   ├── __init__.py              # Application root package
│   ├── main.py                  # FastAPI app factory, CORS middleware, route mounting
│   ├── core/
│   │   ├── __init__.py          # Core package
│   │   ├── auth.py              # Supabase JWT verification & get_current_user dependency
│   │   └── config.py            # Pydantic Settings (DATABASE_URL, SUPABASE_JWT_SECRET, etc.)
│   ├── db/
│   │   ├── __init__.py          # Database package exports
│   │   ├── base.py              # SQLAlchemy 2.x DeclarativeBase for ORM models
│   │   └── session.py           # Engine factory, SessionLocal, get_db dependency
│   ├── models/
│   │   ├── __init__.py          # Model exports (Profile, Task, UserAvailability, UserPreferences)
│   │   ├── profile.py           # Supabase Auth user profile model
│   │   ├── task.py              # Task model with constraints and indexes
│   │   ├── availability.py      # Weekly focus hour availability model
│   │   └── preferences.py       # User scheduling & reminder preferences
│   ├── schemas/
│   │   ├── __init__.py          # Schema exports
│   │   ├── task.py              # Task schemas (CreateTaskRequest, TaskResponse, etc.)
│   │   ├── dashboard.py         # Dashboard schemas (DashboardOverviewResponse, etc.)
│   │   ├── schedule.py          # Schedule schemas (DayScheduleResponse, ScheduleItemResponse)
│   │   └── settings.py          # Settings schemas (SettingsStateResponse, DayAvailabilitySchema)
│   ├── services/
│   │   ├── __init__.py          # Service exports
│   │   ├── task_service.py      # Task domain logic, duration calculations, and queries
│   │   ├── settings_service.py  # Profile, preference, and availability management
│   │   ├── dashboard_service.py # Metrics aggregation, recommendation, and at-risk assessment
│   │   ├── schedule_service.py  # Dynamic daily schedule generation and adaptive updates
│   │   └── scheduling/          # Deterministic Adaptive Scheduling Engine (Phase 3A)
│   │       ├── __init__.py
│   │       ├── schemas.py       # Engine internal DTOs
│   │       ├── scoring.py       # Priority, deadline urgency, difficulty, continuity scoring
│   │       ├── capacity.py      # Working window and focus limits calculation
│   │       ├── risk.py          # Deadline risk analysis
│   │       └── engine.py        # Schedule generation & reschedule decision triggers
│   └── api/
│       ├── __init__.py          # API package
│       └── routes/
│           ├── __init__.py      # Routes package
│           ├── health.py        # /api/health and /api/health/db endpoints
│           ├── tasks.py         # /api/tasks CRUD, filtering, categories endpoints
│           ├── dashboard.py     # /api/dashboard overview, recommendations, at-risk endpoints
│           ├── schedule.py      # /api/schedule timeline and dynamic regeneration endpoints
│           └── settings.py      # /api/settings unified and granular configuration endpoints
├── alembic/
│   ├── env.py                   # Dynamic Alembic environment using app settings
│   ├── script.py.mako           # Revision template
│   └── versions/
│       └── cb3428709a17_create_initial_schema.py # Initial database migration
├── tests/
│   ├── __init__.py              # Test suite package
│   ├── conftest.py              # In-memory DB, auth token helpers, and TestClient fixtures
│   ├── test_health.py           # Health endpoints tests
│   ├── test_auth.py             # Supabase JWT verification and security tests
│   ├── test_models.py           # Model relationships and database constraints tests
│   ├── test_tasks.py            # Task CRUD, filters, sorting, ownership isolation tests
│   ├── test_scheduling.py       # Phase 3A scheduling engine algorithmic tests
│   └── test_api_scheduling.py   # Phase 3B dashboard, schedule, and settings REST API tests
├── alembic.ini                  # Alembic CLI configuration
├── requirements.txt             # Python package dependencies (including pyjwt)
├── .env.example                 # Safe environment template
├── .gitignore                   # Python, virtualenv, and .env ignores
└── README.md                    # Setup and execution guide
```

---

## 🚀 Getting Started

### Prerequisites

- **Python:** 3.11+ (tested on Python 3.11.9)
- **PowerShell** or standard terminal on Windows

---

### 1. Create and Activate Virtual Environment

From the `backend/` directory:

```powershell
# Create virtual environment
python -m venv .venv

# Activate in PowerShell
.\.venv\Scripts\Activate.ps1
```

> **PowerShell Execution Policy Tip:** If you see a script execution error, run:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

---

### 2. Install Dependencies

With the virtual environment active:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 3. Configure Environment Variables

Copy the example environment template:

```powershell
Copy-Item .env.example .env
```

Open `.env` in your editor and configure the parameters:

```env
APP_ENV=development
APP_TITLE=Adaptive Task & Deadline Management API
APP_VERSION=0.1.0

# Database Connection URI (Supabase PostgreSQL)
DATABASE_URL=postgresql+psycopg://postgres.[project-ref]:[db-password]@aws-0-[region].pooler.supabase.com:6543/postgres

# Local Frontend Origin for CORS
FRONTEND_ORIGIN=http://localhost:3000
```

---

### 4. How to Obtain Your Supabase PostgreSQL Connection String

1. Log into your [Supabase Dashboard](https://supabase.com/dashboard).
2. Select your project.
3. In the left sidebar, click **Project Settings** (gear icon) -> **Database**.
4. Scroll down to **Connection Pooling** (recommended for serverless/college apps) or **Connection string**.
5. Select the **URI** tab.
6. Copy the connection string. It will look like:
   ```
   postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
7. Replace `[YOUR-PASSWORD]` with your actual database password.
8. Paste into `backend/.env` as `DATABASE_URL`.
   *(Note: The application automatically handles the `postgresql://` -> `postgresql+psycopg://` dialect mapping for SQLAlchemy 2.x).*

---

### 5. Running the FastAPI Application

Start the local development server with auto-reload:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The server will be accessible at:
- **API Base:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive OpenAPI Docs (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative API Docs (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### 6. Health Check Endpoints

Verify that the process and database are operational:

#### Application Process Health
```powershell
curl http://127.0.0.1:8000/api/health
```
**Expected Response (HTTP 200 OK):**
```json
{
  "status": "ok",
  "service": "adaptive-task-manager-api"
}
```

#### Database Connectivity Check
```powershell
curl http://127.0.0.1:8000/api/health/db
```
- **When connected (HTTP 200 OK):**
  ```json
  {
    "status": "ok",
    "database": "connected"
  }
  ```
- **When unconfigured or unreachable (HTTP 503 Service Unavailable):**
  ```json
  {
    "detail": {
      "status": "error",
      "message": "Database connection unavailable"
    }
  }
  ```
  *(Credentials and internal connection traces are safely concealed).*

---

### 7. Running Automated Tests

Run the test suite with pytest:

```powershell
pytest -v
```

Tests run in isolation and do not require active Supabase credentials (mock sessions test positive connectivity, unconfigured states, and safe failure handling).

---

### 8. Managing Database Migrations with Alembic

Alembic is configured to read `DATABASE_URL` dynamically from `app.core.config.settings` and discover models defined in `app.db.base.Base`.

#### Generating a Migration (Phase 2+)
When new SQLAlchemy models are added:
```powershell
alembic revision --autogenerate -m "create_initial_task_and_profile_tables"
```

#### Applying Migrations
```powershell
alembic upgrade head
```

#### Reverting Migrations
```powershell
alembic downgrade -1
```

---

## 📡 REST API Reference (Phase 2 & Phase 3B)

All endpoints under `/api/tasks`, `/api/dashboard`, `/api/schedule`, and `/api/settings` require a valid Supabase JWT Bearer token:
```http
Authorization: Bearer <supabase_jwt_access_token>
```

### 1. Dashboard Endpoints (`/api/dashboard`)

#### `GET /api/dashboard/overview`
Retrieves aggregated workload, capacity, progress, and at-risk task counts for the authenticated user.
- **Response (HTTP 200 OK):**
```json
{
  "availableTimeHours": 6.5,
  "scheduledWorkloadHours": 3.5,
  "overallProgress": 42,
  "pendingTasksCount": 5,
  "atRiskTasksCount": 1,
  "completedTodayCount": 2
}
```

#### `GET /api/dashboard/recommendation`
Uses the deterministic ranking engine to return the single highest-priority recommended next task.
- **Response (HTTP 200 OK):**
```json
{
  "task": {
    "id": "task-88e89fba",
    "title": "Algorithms Exam Prep",
    "category": "CS",
    "deadline": "2026-10-21T18:00:00Z",
    "priority": "critical",
    "difficulty": "hard",
    "estimatedDuration": 3.0,
    "completedDuration": 1.0,
    "remainingDuration": 2.0,
    "progress": 33,
    "status": "in_progress",
    "createdAt": "2026-10-15T08:00:00Z",
    "updatedAt": "2026-10-15T09:00:00Z"
  },
  "recommendationReason": "High-urgency task due tomorrow with 2.0h remaining; prioritizing prevents cascading delays.",
  "urgencyLabel": "Urgent"
}
```
*(Returns `null` if no active incomplete tasks exist).*

#### `GET /api/dashboard/at-risk`
Returns active tasks whose required hours exceed the user's available capacity before the deadline.
- **Response (HTTP 200 OK):**
```json
[
  {
    "task": {
      "id": "task-102",
      "title": "Distributed Systems Capstone",
      "category": "Engineering",
      "deadline": "2026-10-16T12:00:00Z",
      "priority": "critical",
      "difficulty": "hard",
      "estimatedDuration": 15.0,
      "completedDuration": 0.0,
      "remainingDuration": 15.0,
      "progress": 0,
      "status": "pending"
    },
    "riskLevel": "critical",
    "riskReason": "Requires 15.0h with only 6.5h working capacity before deadline at 2026-10-16T12:00:00Z."
  }
]
```

#### `GET /api/dashboard/upcoming`
Retrieves upcoming active tasks ordered chronologically by deadline.

#### `GET /api/dashboard/schedule`
Retrieves today's scheduled blocks with computed status (`completed`, `current`, `upcoming`).

---

### 2. Schedule Endpoints (`/api/schedule`)

Schedules are calculated dynamically on-the-fly from live tasks, weekly availability windows, and focus-hour limits. No redundant database tables are required.

#### `GET /api/schedule?date=YYYY-MM-DD`
Retrieves conflict-free daily schedule blocks for the requested date (or today in user timezone if omitted).
- **Response (HTTP 200 OK):**
```json
{
  "date": "2026-10-20",
  "dayOfWeek": "Tuesday",
  "formattedDate": "Tuesday, October 20, 2026",
  "isToday": false,
  "items": [
    {
      "id": "block-task-01-0900",
      "taskId": "task-01",
      "title": "Math Assignment",
      "category": "Academics",
      "startTime": "09:00 AM",
      "endTime": "10:30 AM",
      "durationMinutes": 90,
      "status": "pending",
      "isRecommended": true,
      "recommendationReason": "Critical priority task scheduled in first focus block",
      "priority": "critical"
    }
  ],
  "totalScheduledHours": 1.5,
  "availableHours": 6.5
}
```

#### `POST /api/schedule/regenerate`
Recalculates dynamic focus blocks based on current database records.
- **Request Body (optional):**
```json
{
  "date": "2026-10-20"
}
```

#### `GET /api/schedule/update`
Detects whether deadline slips, overdue tasks, or capacity changes warrant adaptive rescheduling.

#### `POST /api/schedule/update/dismiss`
Acknowledges or dismisses the schedule update banner.

---

### 3. Settings Endpoints (`/api/settings`)

#### `GET /api/settings`
Returns unified profile, scheduling preferences, and weekly availability schedule.
- **Response (HTTP 200 OK):**
```json
{
  "profile": {
    "id": "usr_alex_01",
    "name": "Alex Mercer",
    "email": "alex.mercer@example.com",
    "timezone": "America/New_York",
    "role": "student"
  },
  "preferences": {
    "enableDeadlineReminders": true,
    "enableScheduleUpdates": true,
    "defaultTaskDurationMinutes": 60,
    "dailyFocusHoursLimit": 6.5,
    "bufferStrategy": "moderate"
  },
  "availability": [
    {
      "day": "monday",
      "label": "Monday",
      "enabled": true,
      "startTime": "09:00",
      "endTime": "17:00"
    },
    {
      "day": "sunday",
      "label": "Sunday",
      "enabled": false,
      "startTime": "10:00",
      "endTime": "14:00"
    }
  ]
}
```

#### `PATCH /api/settings`
Partially updates profile, preferences, or availability while preserving untouched fields.
- **Request Body Example:**
```json
{
  "profile": {
    "name": "Alex Mercer"
  },
  "preferences": {
    "dailyFocusHoursLimit": 5.0,
    "bufferStrategy": "relaxed"
  }
}
```

#### Granular Settings Routes
- `GET /api/settings/profile` and `PATCH /api/settings/profile`
- `GET /api/settings/preferences` and `PATCH /api/settings/preferences`
- `GET /api/settings/availability` and `PUT /api/settings/availability`
- `POST /api/settings/availability/reset` (Restores standard default 7-day windows)

---

### 4. Date and Timezone Correctness

- **User Timezone Support:** Profile stores standard IANA timezone strings (e.g. `America/New_York`, `Asia/Tokyo`, `UTC`).
- **Graceful Fallback:** If an unrecognized timezone or empty string is provided, system safely falls back to UTC.
- **Local Day Resolution:** All day-based calculations (such as `completedTodayCount` and default schedule date) evaluate against the user's local calendar date, not naive UTC, avoiding premature or delayed date transitions.
- **Storage:** Deadlines and audit timestamps are strictly stored in UTC with timezone awareness.

---

## 🔒 Security Best Practices

- `.env` is explicitly listed in `backend/.gitignore`.
- Database connection strings and credentials must never be committed to Git.
- CORS is strictly configured to `FRONTEND_ORIGIN` (`http://localhost:3000`), avoiding wildcards with credentials.
- All database errors on public endpoints are caught and sanitized to prevent leaking credentials or hostnames.
- Strict multi-tenant isolation: all database queries are scoped to `current_user.id`. Requests cannot manipulate or query other users' tasks or preferences.

