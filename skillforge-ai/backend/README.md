# SkillForge AI Backend

FastAPI service for SkillForge AI.

## Phase 3 status

Authentication and RBAC are in place:

- Argon2 password hashing
- JWT access tokens
- `POST /api/auth/register` (LEARNER only)
- `POST /api/auth/login`
- `GET /api/auth/me`
- Role guards: `LEARNER`, `ADMIN`
- Development admin bootstrap via env (never via public registration)

See [../docs/auth.md](../docs/auth.md) for details.

## Setup

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure repo-root `.env` (never commit real passwords):

```env
DATABASE_URL=postgresql+psycopg://postgres:<YOUR_PASSWORD>@localhost:5432/skillforge_db
JWT_SECRET_KEY=change-me-to-a-long-random-string
```

Optional development admin:

```env
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
BOOTSTRAP_ADMIN_PASSWORD=change-me-dev-only
APP_ENV=development
```

## Migrate

```bash
alembic upgrade head
```

## Seed roles / bootstrap admin

```bash
python -m app.db.seed
```

## Run

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health: http://127.0.0.1:8000/api/health
- Ready: http://127.0.0.1:8000/api/ready
- Docs: http://127.0.0.1:8000/docs

## Test

```bash
pytest -m "not integration"
```

Auth tests use in-memory SQLite — no real PostgreSQL password required.
