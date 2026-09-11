# SkillForge AI — Authentication (Phase 3)

## Overview

Phase 3 adds JWT-based authentication and RBAC using the existing `users` and `roles` tables from Phase 2.

## Roles

| Code | Purpose |
|------|---------|
| `LEARNER` | Default role for public registration |
| `ADMIN` | Administrator (not available via public registration) |

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | Public | Register LEARNER account |
| POST | `/api/auth/login` | Public | Obtain JWT access token |
| GET | `/api/auth/me` | Bearer JWT | Current user profile |
| POST | `/api/auth/logout` | Bearer JWT | Client should discard token |
| GET | `/api/learner/test` | LEARNER | RBAC verification |
| GET | `/api/admin/test` | ADMIN | RBAC verification |

## JWT configuration

Set in local `.env` (never commit real secrets):

```env
JWT_SECRET_KEY=change-me-to-a-long-random-string
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`JWT_SECRET` and `ACCESS_TOKEN_EXPIRE_MINUTES` remain supported as aliases.

## Development admin bootstrap

Public registration **never** creates ADMIN users.

For local development only, set in `.env`:

```env
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
BOOTSTRAP_ADMIN_PASSWORD=change-me-dev-only
APP_ENV=development
```

On API startup (and via `python -m app.db.seed`), an ADMIN user is created or updated. Passwords are never logged.

## Password security

- Argon2 hashing via `passlib`
- Plaintext passwords are never stored or returned
- API responses never include `hashed_password`

## Frontend token storage (MVP)

The React client stores the JWT in `localStorage` under `skillforge_access_token`.

**Production consideration:** prefer HttpOnly secure cookies + CSRF protection; the current approach is modular and easy to replace later.

## Tests

```bash
cd backend
pytest -m "not integration"
```

Auth tests use an in-memory SQLite database — no real PostgreSQL password required.
