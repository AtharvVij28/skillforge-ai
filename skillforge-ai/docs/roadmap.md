# SkillForge AI — Development Roadmap, Risks & Assumptions (Phase 0)

## 1. Phased Roadmap

| Phase | Focus | Exit criteria |
|-------|--------|---------------|
| **0** | Requirements + architecture docs + folder skeleton | Docs approved; structure exists |
| **1** | Project scaffolding, tooling, env, Docker skeleton | `frontend` + `backend` boot empty apps; compose up DB |
| **2** | DB models, migrations, seed skeleton | Tables created; seed script runnable |
| **3** | Auth + RBAC (JWT, hashing, protected routes) | Register/login/me; role guards |
| **4** | Profile + competency framework CRUD | Editable profile; configurable competencies |
| **5** | Skill-gap engine | Explainable gaps API + persistence |
| **6** | Assessment engine | Start/submit/score/attempts |
| **7** | Documents + AI MCQ generation | Upload→chunk→grounded questions |
| **8** | Recommendation engine + mock providers | Ranked recommendations with reasons |
| **9** | Adaptive competency updates | Post-assessment score/gap/recommend refresh |
| **10** | Learner dashboard UI | Charts + loop visibility |
| **11** | Admin dashboard UI | Users, framework, resources, questions, stats |
| **12** | AI assistant UI + grounded backend | Answers tied to user data |
| **13** | Audit logging + security hardening | Audit coverage; upload/CORS limits |
| **14** | Testing & integration bugfix | Pytest + API smoke + critical UI paths |
| **15** | Dockerization & deploy prep | One-command demo; README runbook |

**Rule:** Implement only the requested phase; stop for confirmation after each.

## 2. Assumptions

1. MVP may run with `AI_PROVIDER=mock` and still demonstrate the full loop.
2. iGOT Karmayogi and NSSTA integrations are **mock adapters** until real APIs are provided.
3. Initial roles are only `LEARNER` and `ADMIN`; schema supports more.
4. Job role (e.g., Statistical Officer) is distinct from RBAC role.
5. Competency scores use 0–100 scale; proficiency levels 1–5 are descriptive metadata.
6. PostgreSQL is available via Docker for local development.
7. Single-region, single-tenant deployment is sufficient for MVP.
8. Learner-generated uploads can be deferred; admin uploads suffice for Phase 7 demo.
9. Frontend is SPA talking only to our backend (no secrets in browser).
10. English UI for MVP; i18n can follow.

## 3. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep across 15 phases | Delayed demo | Strict phase gates; MVP non-goals documented |
| LLM dependency for demo | Offline failure | Mock LLM + deterministic engines |
| Weak grounding → bad MCQs | Trust loss | Reject insufficient evidence; admin approval |
| Ambiguous “required” competencies by role | Useless gaps | Seed clear role_competency matrix |
| Auth/security shortcuts | Vulnerability | JWT/RBAC/audit from Phase 3/13; no hardcoded secrets |
| Overfitting UI to mock data | Fragile UX | Clear `is_mock` flags; adapter pattern |
| Vector DB complexity early | Delay | In-memory / lexical retrieval first; interface ready |
| OneDrive/path sync issues on Windows | Tooling friction | Prefer local paths; document Docker volume notes |
| Incomplete profile → poor recommendations | Bad UX | Profile completion % + sensible defaults |
| Assessment gaming / single attempt noise | Volatile scores | Blended updates + confidence |

## 4. Pending Decisions (for later phases)

These do **not** block Phase 0/1; resolve when the phase starts:

1. TypeScript vs JavaScript for frontend (recommendation: **TypeScript** for maintainability).
2. Alembic location: `backend/alembic` vs `database/migrations` (recommendation: Alembic in backend, SQL dumps/docs in `database/`).
3. Access token TTL and whether refresh tokens ship in MVP.
4. Whether learners can upload materials or only admins (MVP default: **admin only**).
5. Choice of chart library (Recharts recommended).
6. File storage: local disk vs S3-compatible (MVP: **local volume**).
7. pgvector vs external vector store timing (MVP: memory/lexical).

## 5. Definition of Done (Final MVP)

Demonstrable loop:

`Profile → Competency profile → Skill gaps → Recommendations → Learn → AI assessment → Score update → Gaps change → Recommendations adapt`

Works with seed/mock data and without live iGOT/NSSTA APIs.

---

*Document status: Phase 0.*
