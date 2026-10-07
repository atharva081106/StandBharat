# StandBharat

An autonomous AI marketing team platform. Phase 1 Implementation.

## Prerequisites
- Node.js (v22+)
- Python (v3.10+)
- Docker & Docker Compose

## Infrastructure Setup
1. Copy environment variables: `cp .env.example .env` (update if needed)
2. Start infrastructure: `docker-compose up -d`

## Backend Setup
1. `cd backend`
2. `python -m venv venv`
3. Activate virtual environment (`.\venv\Scripts\activate` on Windows, `source venv/bin/activate` on Unix)
4. `pip install -r requirements.txt` (or install dependencies manually as listed in `pyproject.toml`/`requirements.txt`)
5. Run migrations: `alembic upgrade head`

### Backend Development Commands
- Start API server: `uvicorn app.main:app --reload`
- Start Celery worker: `celery -A app.workers.celery_worker worker --loglevel=info` (on Windows use `--pool=solo`)
- Run tests: `pytest`

## Frontend Setup
1. `cd frontend`
2. `npm install`

### Frontend Development Commands
- Start development server: `npm run dev`

## Overall Architecture
- **Frontend**: Next.js, React, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Celery, Redis
- **Multi-tenancy**: Workspace and Brand isolation
