# SkillForge AI

AI-enabled Skill Intelligence and Personalized Learning Platform for India’s Official Statistical System.

**Learning loop:** Profile → Assess → Recommend → Learn → Assess again

## Status

**Phase 8 in progress** — assessments, competency updates, and learning paths with study material.

Loop: Profile → Skill gaps → Assessment → Score update → Learning path.

Next: Phase 9 polish / Phase 12 assistant. Live MCQ writing needs `AI_PROVIDER=openai` and `LLM_API_KEY` in `.env`.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/architecture.md](docs/architecture.md) | System architecture |
| [docs/database.md](docs/database.md) | Data model |
| [docs/api.md](docs/api.md) | API map |
| [docs/ai.md](docs/ai.md) | AI design |
| [docs/roadmap.md](docs/roadmap.md) | Phased roadmap |

## Quick start (Phase 2)

### 1. Environment

Copy `.env.example` to `.env` if needed, then set **locally**:

```env
DATABASE_URL=postgresql+psycopg://postgres:<YOUR_PASSWORD>@localhost:5432/skillforge_db
```

Replace `<YOUR_PASSWORD>` in your editor. Never paste the real password into chat, commits, or docs.

`.env` is gitignored.

### 2. PostgreSQL (local Windows install)

- Server running on `localhost:5432`
- Database: `skillforge_db`
- Docker is **not** required for local Phase 2 development

Create the DB once (password prompted by `psql`, not stored here):

```bash
psql -U postgres -c "CREATE DATABASE skillforge_db;"
```

### 3. Backend

```bash
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health: http://127.0.0.1:8000/api/health  
- Ready: http://127.0.0.1:8000/api/ready  
- Docs: http://127.0.0.1:8000/docs  

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173

## Stack

- Frontend: React, Vite, TypeScript, Tailwind CSS, React Router, Axios, Recharts
- Backend: Python, FastAPI, Pydantic Settings, SQLAlchemy 2.x, Alembic
- Database: PostgreSQL 18 (local) — Docker Compose kept for future deploy only
- AI / integrations: mock-ready configuration via `.env`

## Repository layout

```
skillforge-ai/
├── frontend/
├── backend/
│   └── alembic/          # schema migrations
├── database/
│   └── seed/             # future seed fixtures
├── docs/
├── docker-compose.yml    # optional / future
├── .env.example
└── README.md
```
