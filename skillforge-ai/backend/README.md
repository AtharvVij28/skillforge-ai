# SkillForge AI Backend

FastAPI service for SkillForge AI.

## Phase 2 status

PostgreSQL foundation is in place:

- SQLAlchemy 2.x models + relationships
- Alembic migrations (`alembic/`)
- `/api/health` (liveness) and `/api/ready` (DB connectivity)
- Seed scaffold under `app/db/seed.py` and `../database/seed/`

## Setup

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure the repo-root `.env` (never commit real passwords):

```env
DATABASE_URL=postgresql+psycopg://postgres:<YOUR_PASSWORD>@localhost:5432/skillforge_db
```

Replace `<YOUR_PASSWORD>` locally. Do not paste the password into chat or docs.

Ensure the database `skillforge_db` exists in PostgreSQL 18.

## Migrate

From `backend/`:

```bash
alembic upgrade head
```

## Run

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health: http://127.0.0.1:8000/api/health
- Ready: http://127.0.0.1:8000/api/ready
- OpenAPI: http://127.0.0.1:8000/docs

## Test

```bash
pytest
```

Live DB integration test:

```bash
pytest -m integration
```

Skip DB tests: `SKIP_DB_TESTS=1 pytest`
