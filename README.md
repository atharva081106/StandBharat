<div align="center">
  <h1>🚀 StandBharat — AI CMO Platform</h1>
  <p><strong>Your Autonomous AI Marketing Team for Real Growth</strong></p>

  <p>
    <a href="#features"><img src="https://img.shields.io/badge/Features-✨-blue?style=for-the-badge&color=800020" alt="Features"></a>
    <a href="#architecture"><img src="https://img.shields.io/badge/Architecture-🏗️-orange?style=for-the-badge&color=111111" alt="Architecture"></a>
    <a href="#setup-guide"><img src="https://img.shields.io/badge/Setup-🛠️-green?style=for-the-badge&color=E8E4DC&labelColor=111111" alt="Setup"></a>
  </p>
</div>

---

## 🌟 What is StandBharat?

StandBharat is an enterprise-grade AI marketing platform that acts as your **Autonomous AI CMO**. It replaces fragmented marketing workflows by deploying specialized AI agents that orchestrate campaigns, generate content, analyze competitors, and drive revenue—all in one unified command center.

### Core Capabilities
- 🧠 **Brand Brain**: Centralized intelligence that learns your brand voice, assets, and guidelines.
- 🤖 **Specialized Agents**: 
  - **Growth Agent**: Identifies acquisition opportunities and scales campaigns.
  - **Content Agent**: Generates multi-format, brand-aligned marketing collateral.
  - **Analytics Agent**: Processes real-time data for actionable insights.
  - **Competitor Agent**: Monitors rival strategies and market gaps.
- ⚙️ **The Execution Loop**: Plan $\rightarrow$ Generate $\rightarrow$ Review $\rightarrow$ Publish $\rightarrow$ Analyze.

---

## 🏗️ Architecture Overview

The platform is designed with a modern, scalable tech stack separating the client application from the heavy AI processing layers.

### **Frontend (Next.js + Tailwind CSS)**
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS with custom glassmorphism and premium aesthetics (`#800020` Burgundy primary).
- **State Management**: React Context via structured Providers (`AppProvider`, `MockProvider`).
- **Data Mode**: Seamlessly toggle between `mock` and `api` data via environment variables.

### **Backend (FastAPI + Python + Postgres)**
- **Framework**: FastAPI for high-performance async endpoints.
- **Database**: PostgreSQL (via SQLAlchemy & Alembic) for relational entity storage.
- **Task Queue**: Celery + Redis for asynchronous AI orchestration and background jobs.
- **AI Integration**: Custom Agent framework for reasoning and execution.

---

## 🛠️ Step-by-Step Setup Guide

Follow these instructions to get the complete StandBharat platform running on your local machine.

### Prerequisites
Before you begin, ensure you have the following installed:
- [Node.js](https://nodejs.org/) (v22+)
- [Python](https://www.python.org/) (v3.10+)
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (for Redis & PostgreSQL)
- [Git](https://git-scm.com/)

### 1. Infrastructure Setup (Database & Cache)
We use Docker Compose to instantly spin up PostgreSQL and Redis.

```bash
# Clone the repository
git clone https://github.com/atharva081106/StandBharat.git
cd StandBharat

# Copy environment variables
cp .env.example .env

# Start the infrastructure containers in the background
docker-compose up -d
```
> **Note:** Ensure Docker Desktop is running before executing `docker-compose up`.

### 2. Backend Setup (FastAPI & Celery)
The backend manages the API, database models, and AI agent execution.

```bash
# Navigate to the backend directory
cd backend

# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations to set up the schema
alembic upgrade head
```

#### Running the Backend Services
You need two terminal windows for the backend (both with the `venv` activated):

**Terminal 1 (API Server):**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 (Celery Background Worker):**
```bash
cd backend
# On Windows:
celery -A app.workers.celery_worker worker --loglevel=info --pool=solo
# On macOS/Linux:
celery -A app.workers.celery_worker worker --loglevel=info
```

### 3. Frontend Setup (Next.js)
The frontend powers the sleek Landing Page and the Command Center dashboard.

```bash
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install Node modules
npm install

# Start the development server
npm run dev
```

The application will now be available at **`http://localhost:3000`**!

---

## 📂 Project Structure

```text
StandBharat/
├── backend/                   # Python FastAPI Backend
│   ├── app/
│   │   ├── api/               # REST API Routers
│   │   ├── agents/            # Specialized AI Agents & Orchestrator
│   │   ├── models/            # SQLAlchemy Database Models
│   │   ├── schemas/           # Pydantic Validation Schemas
│   │   └── workers/           # Celery Tasks
│   ├── migrations/            # Alembic Database Migrations
│   └── scripts/               # Test & Seed Scripts
│
├── frontend/                  # Next.js React Frontend
│   ├── app/                   # App Router Pages (Dashboard, Landing)
│   ├── components/            # Reusable UI Components & Modals
│   ├── lib/                   # Utility Functions & API Client
│   └── public/                # Static Assets (Images, SVGs)
│
└── docker-compose.yml         # Infrastructure Config (Postgres, Redis)
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests (Playwright)
```bash
cd frontend
npx playwright test
```

---

<div align="center">
  <p>Built with ❤️ for the future of marketing.</p>
</div>
