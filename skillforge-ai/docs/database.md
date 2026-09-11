# SkillForge AI — Database Design (Phase 0)

## 1. Design Principles

- Normalized PostgreSQL schema with foreign keys and timestamps
- Soft-delete only where audit/history requires retention (prefer audit_logs for events)
- Competency framework is **data-driven** (not hardcoded in application logic)
- Scores stored as numeric (0–100) with optional proficiency level mapping (1–5)
- Mock course catalogs stored as `learning_resources` with `provider` discriminator

## 2. Entity-Relationship Overview

```
roles ──────────────┐
departments ────────┤
                    ▼
users ◄──── user_profiles
  │              │
  │              └──► user_competencies ◄── competencies ◄── competency_categories
  │                              ▲
  │                              │
  │                     role_competencies (required levels)
  │
  ├── learning_history ──► learning_resources
  ├── recommendations ───► learning_resources / competencies
  ├── documents ──► document_chunks
  ├── questions ──► competencies / document_chunks
  ├── assessments ──► assessment_questions ──► questions
  │         └──► assessment_attempts ──► assessment_answers
  └── audit_logs
```

## 3. Core Tables

### `roles`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID/PK | |
| code | VARCHAR unique | `LEARNER`, `ADMIN`, future roles |
| name | VARCHAR | |
| description | TEXT | |
| created_at / updated_at | TIMESTAMPTZ | |

### `departments`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| code | VARCHAR unique | e.g. `MOSPI`, `NSO` |
| name | VARCHAR | |
| description | TEXT | |
| created_at / updated_at | TIMESTAMPTZ | |

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| email | VARCHAR unique | login identifier |
| hashed_password | VARCHAR | never plaintext |
| full_name | VARCHAR | |
| role_id | FK → roles | RBAC |
| department_id | FK → departments nullable | |
| is_active | BOOLEAN | |
| last_login_at | TIMESTAMPTZ nullable | |
| created_at / updated_at | TIMESTAMPTZ | |

### `user_profiles`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| user_id | FK unique → users | 1:1 |
| designation | VARCHAR | |
| job_role | VARCHAR | role title / assignment role |
| assignment | TEXT | current posting / responsibilities |
| education | TEXT | |
| years_of_experience | INT | |
| technical_skills | JSONB / TEXT[] | freeform tags |
| statistical_skills | JSONB / TEXT[] | |
| digital_skills | JSONB / TEXT[] | |
| managerial_skills | JSONB / TEXT[] | |
| behavioural_skills | JSONB / TEXT[] | |
| previous_training | JSONB | list of prior courses |
| career_goals | TEXT | |
| profile_completion_pct | INT | computed/cached |
| created_at / updated_at | TIMESTAMPTZ | |

### `competency_categories`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| code | VARCHAR unique | `STATISTICAL`, `TECHNICAL`, etc. |
| name | VARCHAR | |
| description | TEXT | |
| sort_order | INT | |

### `competencies`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| code | VARCHAR unique | stable competency ID |
| name | VARCHAR | |
| category_id | FK | |
| description | TEXT | |
| proficiency_levels | JSONB | descriptors for levels 1–5 |
| default_priority | VARCHAR | LOW/MEDIUM/HIGH |
| is_active | BOOLEAN | |
| created_at / updated_at | TIMESTAMPTZ | |

### `role_competencies`
Required proficiency by job role / designation template.

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| role_code | VARCHAR | e.g. `STATISTICAL_OFFICER` (job role, not RBAC) |
| department_id | FK nullable | optional scoping |
| competency_id | FK | |
| required_score | NUMERIC(5,2) | 0–100 |
| priority | VARCHAR | |
| relevance_weight | NUMERIC | for ranking |
| UNIQUE(role_code, department_id, competency_id) | | |

### `user_competencies`
Living competency scores.

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| user_id | FK | |
| competency_id | FK | |
| current_score | NUMERIC(5,2) | 0–100 |
| confidence | NUMERIC(5,2) | 0–1 |
| source | VARCHAR | `PROFILE`, `ASSESSMENT`, `MANUAL` |
| last_assessed_at | TIMESTAMPTZ | |
| explanation | TEXT | latest score rationale |
| UNIQUE(user_id, competency_id) | | |
| created_at / updated_at | TIMESTAMPTZ | |

### `learning_resources`
Catalog (mock iGOT / NSSTA + internal).

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| external_id | VARCHAR nullable | provider course id |
| title | VARCHAR | |
| provider | VARCHAR | `IGOT`, `NSSTA`, `INTERNAL` |
| description | TEXT | |
| url | VARCHAR nullable | |
| competency_ids | via junction `learning_resource_competencies` | |
| estimated_hours | NUMERIC | |
| difficulty | VARCHAR | |
| is_mock | BOOLEAN default true | MVP flag |
| metadata | JSONB | |
| created_at / updated_at | TIMESTAMPTZ | |

### `learning_resource_competencies`
| resource_id | competency_id | weight |

### `learning_history`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| user_id | FK | |
| resource_id | FK | |
| status | VARCHAR | `RECOMMENDED`, `IN_PROGRESS`, `COMPLETED`, `SKIPPED` |
| progress_pct | INT | |
| started_at / completed_at | TIMESTAMPTZ | |
| notes | TEXT | |

### `documents`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| uploaded_by | FK → users | |
| filename | VARCHAR | |
| content_type | VARCHAR | |
| storage_path | VARCHAR | |
| status | VARCHAR | `UPLOADED`, `PROCESSED`, `FAILED` |
| page_count | INT nullable | |
| metadata | JSONB | |
| created_at / updated_at | TIMESTAMPTZ | |

### `document_chunks`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| document_id | FK | |
| chunk_index | INT | |
| content | TEXT | |
| page_number | INT nullable | |
| section_title | VARCHAR nullable | |
| token_count | INT | |
| embedding_ref | VARCHAR nullable | pointer into vector store |

### `questions`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| stem | TEXT | question text |
| options | JSONB | `[{key, text}]` |
| correct_option | VARCHAR | |
| explanation | TEXT | |
| difficulty | VARCHAR | |
| competency_id | FK | |
| source_document_id | FK nullable | |
| source_chunk_id | FK nullable | |
| source_excerpt | TEXT | grounding evidence |
| generation_method | VARCHAR | `MANUAL`, `AI` |
| is_approved | BOOLEAN | admin review |
| created_by | FK nullable | |
| created_at / updated_at | TIMESTAMPTZ | |

### `assessments`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| title | VARCHAR | |
| description | TEXT | |
| time_limit_minutes | INT nullable | |
| created_by | FK | |
| is_published | BOOLEAN | |
| created_at / updated_at | TIMESTAMPTZ | |

### `assessment_questions`
| assessment_id | question_id | sort_order | points |

### `assessment_attempts`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| assessment_id | FK | |
| user_id | FK | |
| started_at | TIMESTAMPTZ | |
| submitted_at | TIMESTAMPTZ nullable | |
| total_score | NUMERIC | |
| percentage | NUMERIC | |
| competency_breakdown | JSONB | |
| strengths | JSONB | |
| weaknesses | JSONB | |
| feedback_summary | TEXT | |
| next_action | TEXT | |
| status | VARCHAR | `IN_PROGRESS`, `SUBMITTED`, `EXPIRED` |

### `assessment_answers`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| attempt_id | FK | |
| question_id | FK | |
| selected_option | VARCHAR | |
| is_correct | BOOLEAN | |
| points_awarded | NUMERIC | |
| feedback | TEXT | |

### `recommendations`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| user_id | FK | |
| resource_id | FK | |
| competency_id | FK | |
| relevance_score | NUMERIC | |
| gap_at_generation | NUMERIC | |
| expected_benefit | TEXT | |
| reason | TEXT | explainability blob |
| estimated_effort_hours | NUMERIC | |
| rank | INT | |
| status | VARCHAR | `ACTIVE`, `DISMISSED`, `COMPLETED` |
| generated_at | TIMESTAMPTZ | |
| expires_at | TIMESTAMPTZ nullable | |

### `skill_gap_snapshots` (recommended)
Optional persistence of last gap analysis for dashboards/audit.

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| user_id | FK | |
| competency_id | FK | |
| current_score | NUMERIC | |
| required_score | NUMERIC | |
| gap | NUMERIC | |
| priority | VARCHAR | |
| confidence | NUMERIC | |
| explanation | TEXT | |
| computed_at | TIMESTAMPTZ | |

### `audit_logs`
| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| user_id | FK nullable | system actions allowed |
| action | VARCHAR | e.g. `LOGIN`, `PROFILE_UPDATE` |
| entity_type | VARCHAR | |
| entity_id | VARCHAR | |
| metadata | JSONB | |
| ip_address | VARCHAR nullable | |
| created_at | TIMESTAMPTZ | append-only |

## 4. Indexing Strategy (MVP)

- `users.email` unique
- `user_competencies (user_id, competency_id)` unique
- `assessment_attempts (user_id, assessment_id, submitted_at)`
- `recommendations (user_id, status, rank)`
- `audit_logs (user_id, created_at)`, `(action, created_at)`
- `document_chunks (document_id, chunk_index)`

## 5. Migrations & Seed

- Migrations: Alembic under `database/migrations` (or `backend/alembic` linked from docs)
- Seed: `database/seed/` — departments, roles, competencies, sample users, mock courses, sample questions

## 6. ER Notes

- RBAC `roles` ≠ job `role_code` in `role_competencies` (keep separate to avoid confusion)
- Vector embeddings may live outside Postgres initially (file/JSON mock or pgvector later); `embedding_ref` keeps the schema ready

---

*Document status: Phase 0.*
