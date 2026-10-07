# StandBharat Development Guide

## Architecture Overview

StandBharat uses a modern API-driven architecture.
- **Frontend**: Next.js (App Router), React, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, Celery
- **Database**: PostgreSQL with pgvector (via Docker)
- **Cache / Message Broker**: Redis (via Docker)

## Local Development Setup

### 1. Requirements

- Docker Desktop / Engine
- Python 3.10+
- Node.js 18+

### 2. Start Infrastructure

Start the PostgreSQL and Redis containers using Docker Compose:

```bash
docker compose up -d
```

### 3. Backend Setup

Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate # Unix
pip install -r requirements.txt
```

Run database migrations:

```bash
alembic upgrade head
```

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql://standbharat_user:standbharat_password@localhost:5432/standbharat_db
REDIS_URL=redis://localhost:6380/0
SECRET_KEY=super-secret-key-change-in-prod
ALGORITHM=HS256
OPENAI_API_KEY=your-openai-api-key-here
```

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload --port 8000
```

Start the Celery worker (in a separate terminal).
**CRITICAL WINDOWS NOTE**: StandBharat uses a Docker Redis 7 container mapped to `localhost:6380`. Do NOT use the Windows Memurai (Redis 5) instance on `localhost:6379`, as it lacks support for the `HELLO` command required by modern Kombu.

```bash
cd backend
venv\Scripts\activate
venv\Scripts\celery.exe -A app.core.celery_app worker --loglevel=info -P solo
```

Start Celery Beat to execute scheduled tasks (e.g., the autonomous orchestrator tick):

```bash
cd backend
venv\Scripts\activate
venv\Scripts\celery.exe -A app.core.celery_app beat --loglevel=info
```

### Infrastructure Verification

To verify your infrastructure is working correctly:

1. **Redis Connectivity**:
   ```bash
   redis-cli -p 6380 PING
   # Expected: PONG
   ```

2. **Worker Connectivity**:
   ```bash
   cd backend
   venv\Scripts\celery.exe -A app.core.celery_app inspect ping
   # Expected: OK (pong)
   ```

### Troubleshooting Redis/Celery

If your Celery worker fails with `kombu.exceptions.OperationalError: unknown command 'HELLO'`:
- Verify your `.env` contains `REDIS_URL=redis://localhost:6380/0`
- Ensure your `docker-compose.yml` maps `6380:6379`
- Do not point StandBharat to `localhost:6379` on Windows if you have Memurai installed.

### 4. Frontend Setup

The frontend supports two modes: **mock** and **api**.

- **mock**: Uses in-memory hardcoded data. (Good for UI development without backend).
- **api**: Connects to the real FastAPI backend.

To run with real data, create `.env.local` in the `frontend/` directory:

```env
NEXT_PUBLIC_DATA_MODE=api
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Install dependencies and start:

```bash
cd frontend
npm install
npm run dev -p 5000
```

## Running Tests

To run the backend tests:

```bash
cd backend
pytest -v
```

During tests, the database should ideally be a separate test database, and Celery tasks run synchronously (`task_always_eager = True`).
