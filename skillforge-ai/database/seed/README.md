# Seed data

Executable seed: `backend/app/db/seed.py`

## What it seeds (Phase 4)

1. RBAC roles: `LEARNER`, `ADMIN`
2. Sample departments (`MOSPI`, `NSO`, `NSSTA`, `DATA_ANALYTICS`)
3. Competency categories + competencies
4. Job-role competency requirements (`STATISTICAL_OFFICER`, `DATA_ANALYST`)

## Rules

- Mark mock/sample learning resources with `is_mock=true` when those are added in later phases.
- Do **not** treat mock course rows as live iGOT/NSSTA API responses.
- Never put real database passwords in seed files.
- Framework seed is idempotent and also runs on API startup when the database is available.
