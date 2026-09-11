# Seed data (Phase 2 scaffold)

This folder holds **future** seed scripts and fixtures.

## Rules

- Seed data for MVP catalogs (roles, departments, competencies, mock iGOT/NSSTA courses) will be added in later phases.
- Mark mock/sample learning resources with `is_mock=true` in the database.
- Do **not** treat mock course rows as live iGOT/NSSTA API responses.
- Never put real database passwords in seed files.

## Planned seed targets

1. RBAC roles: `LEARNER`, `ADMIN`
2. Departments (sample)
3. Competency categories + competencies
4. Role competency requirements (job-role based)
5. Mock learning resources (`provider=IGOT|NSSTA`, `is_mock=true`)

Executable seed entrypoint (stub): `backend/app/db/seed.py`
