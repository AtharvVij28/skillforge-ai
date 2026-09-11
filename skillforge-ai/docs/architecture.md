# SkillForge AI — System Architecture (Phase 0)

## 1. Problem Summary

India’s Official Statistical System is adopting AI/ML, big data, GIS, cloud, and modern statistical methods. Officials need continuous, role-specific upskilling. iGOT Karmayogi and NSSTA provide content, but there is no intelligent layer to:

- assess competency gaps against role/department requirements
- prioritize skills with explainable rationale
- recommend personalized learning paths
- measure outcomes and adapt over time

**SkillForge AI** closes this loop:

```
PROFILE → ASSESS → RECOMMEND → LEARN → ASSESS AGAIN
```

## 2. Architecture Goals

| Goal | How the MVP addresses it |
|------|--------------------------|
| Functional end-to-end loop | Seed data + mock providers + real engines (gap, assess, recommend, adapt) |
| Explainability | Every gap, recommendation, and score update carries human-readable reasons |
| Maintainability | Modular backend services; thin API routes; replaceable AI/providers |
| Security | JWT + RBAC + validation + audit from day one |
| Cloud-ready | Docker Compose, env-based config, no hardcoded secrets |
| Extensibility | Provider interfaces for iGOT/NSSTA; LLM/embeddings abstractions |

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (React)                          │
│  Learner UI │ Admin UI │ AI Assistant │ Auth (JWT in memory/store)│
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / REST (Axios)
┌────────────────────────────▼────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│                   FastAPI routers (/api/*)                      │
│         Auth middleware │ RBAC │ validation │ CORS              │
└──────┬──────────┬──────────┬──────────┬──────────┬──────────────┘
       │          │          │          │          │
┌──────▼──┐ ┌─────▼────┐ ┌───▼────┐ ┌───▼────┐ ┌──▼───────────┐
│ Profile │ │Competency│ │ Skill  │ │Assess- │ │ Document /   │
│ Service │ │ Framework│ │ Gap    │ │ ment   │ │ AI Question  │
│         │ │ Service  │ │ Engine │ │ Engine │ │ Generation   │
└─────────┘ └──────────┘ └───┬────┘ └───┬────┘ └──┬───────────┘
                             │          │         │
                    ┌────────▼──────────▼─────────▼────────┐
                    │         Adaptive Learning Layer       │
                    │  (score update → gap → recommend)     │
                    └────────┬──────────────────┬───────────┘
                             │                  │
                    ┌────────▼────────┐ ┌───────▼────────────┐
                    │ Recommendation  │ │ AI Assistant        │
                    │ Engine          │ │ (grounded Q&A)      │
                    └────────┬────────┘ └───────┬────────────┘
                             │                  │
                    ┌────────▼──────────────────▼────────────┐
                    │     Integration Adapters (mock MVP)    │
                    │  CourseProvider → IGOT | NSSTA (mock)  │
                    │  LLMProvider | EmbeddingStore (swappable)│
                    └────────────────────┬───────────────────┘
                                         │
                    ┌────────────────────▼───────────────────┐
                    │         PostgreSQL + Audit Log         │
                    └────────────────────────────────────────┘
```

## 4. Logical Modules

| Module | Responsibility | Location |
|--------|----------------|----------|
| Auth / RBAC | Register, login, JWT, role checks | `backend/app/api`, `core`, `services` |
| Profile | Living competency profile CRUD | `services/profile_service` |
| Competency Framework | Configurable competencies & role requirements | `services/competency_service` |
| Skill Gap Engine | Explainable gap calculation | `services/skill_gap_service` |
| Assessment Engine | Quizzes, scoring, attempts | `assessments/` |
| Document Processing | PDF/DOCX/TXT extract, chunk, metadata | `document_processing/` |
| AI Layer | LLM + embeddings abstractions, MCQ gen, assistant | `ai/` |
| Recommendations | Ranked learning opportunities + reasons | `services/recommendation_service` |
| Integrations | Mock iGOT / NSSTA providers | `integrations/` |
| Adaptive Learning | Post-assessment score & ranking updates | `services/adaptive_service` |
| Audit | Immutable event trail | `services/audit_service` |
| Frontend | Dashboards, flows, charts | `frontend/src` |

**Principle:** API routes orchestrate; business logic lives in services; AI logic is never embedded in route handlers.

## 5. Deployment Topology (MVP)

```
docker-compose
├── frontend   (Vite/Nginx or Vite dev)
├── backend    (Uvicorn / FastAPI)
├── db         (PostgreSQL)
└── (optional later) vector sidecar / redis
```

Local development may run frontend + backend on host with PostgreSQL in Docker.

## 6. Security Architecture (baseline)

- Passwords: bcrypt/argon2 via passlib
- Auth: short-lived JWT access tokens; refresh optional in later hardening
- Authorization: role claims (`LEARNER`, `ADMIN`) checked per route
- Uploads: MIME/extension allowlist, size limits, virus-scan hook later
- Secrets: environment only; never in frontend bundles
- ORM parameterized queries (SQLAlchemy)
- CORS allowlist via config
- Audit log for sensitive actions

## 7. Non-Goals for MVP

- Live iGOT / NSSTA production APIs
- Multi-tenant SSO (e.g., Parichay)
- Real-time collaboration
- Mobile native apps
- Production-grade vector DB HA
- Full LMS content hosting (we recommend + link out)

## 8. Success Path (demo)

1. User registers / logs in as LEARNER  
2. Completes / edits profile  
3. System maps competencies & computes skill gaps (with explanations)  
4. Recommendations appear (mock iGOT/NSSTA) with reasons  
5. Admin uploads material → AI generates grounded MCQs  
6. Learner takes assessment → scores update competencies  
7. Gaps shrink / grow → recommendations re-rank  
8. Assistant answers grounded questions about the user’s state  

---

*Document status: Phase 0 — approved for incremental implementation.*
