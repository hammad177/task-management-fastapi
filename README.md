# Task Management FastAPI

A REST API for task management with user authentication, built with FastAPI using a clean, layered architecture.

## Tech Stack

- **Framework:** FastAPI (Python 3.10+)
- **Database:** SQLite (async via aiosqlite)
- **ORM:** SQLAlchemy 2.0+ (async)
- **Auth:** JWT + bcrypt password hashing

## Features

- JWT-based authentication (register, login, password change)
- Full task CRUD, scoped to the logged-in user
- Task priority levels (low, medium, high, urgent) and completion toggling
- Search, filtering, and pagination on tasks
- Unified success/error response format with global exception handling

## Architecture

```
Request → Routes → Controllers → Services → Repositories → Models → Database
```

## Installation

```bash
git clone <repo-url>
cd task_management_fast_api
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your own values.

## Environment Variables (`.env`)

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./task_management.db
DB_ECHO=True
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE=3600

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=Task Management API
DESCRIPTION=A FastAPI application for managing tasks
DEBUG=False
API_VERSION=v1
```

## Running

```bash
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

## API Endpoints

**Auth (public)**

- `POST /api/users/register`
- `POST /api/users/login`

**Users** (JWT required)

- `GET /api/users/me`
- `GET /api/users/`
- `GET /api/users/{user_id}`
- `PUT /api/users/me`
- `DELETE /api/users/me`
- `PATCH /api/users/me/password`

**Tasks** (JWT required)

- `POST /api/tasks/`
- `GET /api/tasks/` — supports filters (priority, is_done, search, pagination)
- `GET /api/tasks/{task_id}`
- `PUT /api/tasks/{task_id}`
- `PATCH /api/tasks/{task_id}/toggle`
- `DELETE /api/tasks/{task_id}`

## Quick Test

```bash
# Register
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"TestPass123"}'

# Login
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"TestPass123"}'
```

Or use the interactive docs at `/docs` — register, log in, click "Authorize", and test the protected routes directly.
