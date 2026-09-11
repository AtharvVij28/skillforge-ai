# SkillForge AI — API Architecture (Phase 0)

## 1. Conventions

| Item | Convention |
|------|------------|
| Base path | `/api` |
| Format | JSON |
| Auth | `Authorization: Bearer <JWT>` |
| Errors | `{ "detail": "...", "code": "OPTIONAL_CODE" }` |
| Pagination | `?page=1&page_size=20` → `{ items, total, page, page_size }` |
| Timestamps | ISO-8601 UTC |
| IDs | UUID strings |

Validation via Pydantic. OpenAPI auto-generated at `/docs` (Swagger) and `/redoc`.

## 2. Route Map

### Auth — `/api/auth`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | Public | Create LEARNER (admin creation via admin API) |
| POST | `/login` | Public | Return access token + user summary |
| POST | `/logout` | Auth | Client discard + optional audit |
| GET | `/me` | Auth | Current user + role |

### Users — `/api/users`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | ADMIN | List users (paginated, filters) |
| GET | `/{user_id}` | ADMIN or self | User detail |
| PATCH | `/{user_id}` | ADMIN | Activate/deactivate, role change |

### Profile — `/api/profile`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | LEARNER/ADMIN | Own profile |
| PUT | `/` | LEARNER/ADMIN | Update profile |
| GET | `/{user_id}` | ADMIN | View another profile |
| GET | `/completion` | Auth | Profile completion metrics |

### Competencies — `/api/competencies`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Auth | List competencies (+ category filter) |
| GET | `/categories` | Auth | List categories |
| GET | `/{id}` | Auth | Detail |
| POST | `/` | ADMIN | Create competency |
| PUT | `/{id}` | ADMIN | Update |
| DELETE | `/{id}` | ADMIN | Soft-deactivate |
| GET | `/framework` | Auth | Full framework tree |
| PUT | `/role-requirements` | ADMIN | Upsert role competency requirements |

### Skills / Gaps — `/api/skills`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/me` | Auth | User competency scores |
| POST | `/gaps/analyze` | Auth | Compute & return explainable gaps |
| GET | `/gaps` | Auth | Latest gap snapshot |
| GET | `/gaps/{user_id}` | ADMIN | Gaps for a user |

### Assessments — `/api/assessments`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Auth | List available assessments |
| GET | `/{id}` | Auth | Assessment detail (no answers for learners) |
| POST | `/` | ADMIN | Create assessment |
| POST | `/{id}/publish` | ADMIN | Publish |
| POST | `/{id}/start` | Auth | Start attempt |
| POST | `/attempts/{attempt_id}/submit` | Auth | Submit answers |
| GET | `/attempts/{attempt_id}` | Auth | Attempt + results |
| GET | `/attempts` | Auth | Own attempt history |
| GET | `/questions` | ADMIN | List/review questions |
| PATCH | `/questions/{id}` | ADMIN | Approve/edit question |

### Documents — `/api/documents`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/upload` | ADMIN (MVP) | Upload PDF/DOCX/TXT |
| GET | `/` | ADMIN | List documents |
| GET | `/{id}` | ADMIN | Metadata + status |
| POST | `/{id}/process` | ADMIN | Extract + chunk |
| POST | `/{id}/generate-questions` | ADMIN | AI MCQ generation |
| DELETE | `/{id}` | ADMIN | Remove |

### Recommendations — `/api/recommendations`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Auth | Active recommendations for user |
| POST | `/generate` | Auth | Regenerate from current gaps |
| POST | `/{id}/dismiss` | Auth | Dismiss |
| POST | `/{id}/start` | Auth | Mark learning started |

### Learning — `/api/learning`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/resources` | Auth | Catalog (filter by provider/competency) |
| GET | `/history` | Auth | User learning history |
| PATCH | `/history/{id}` | Auth | Update progress/status |

### Admin — `/api/admin`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/stats` | ADMIN | Aggregate competency / usage stats |
| GET | `/departments` | ADMIN | Department list/CRUD subset |
| GET | `/audit` | ADMIN | Audit log query |
| GET | `/dashboard` | ADMIN | Admin dashboard payload |

### Assistant — `/api/assistant`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/chat` | Auth | Grounded Q&A turn |
| GET | `/history` | Auth | Optional conversation history (MVP may be session-only) |

## 3. Example Explainable Payloads

### Skill gap item
```json
{
  "competency_id": "...",
  "competency_name": "Python for Data Analysis",
  "current_score": 52,
  "required_score": 80,
  "gap": 28,
  "priority": "HIGH",
  "confidence": 0.78,
  "explanation": "Your current competency estimate is below the level expected for your current role. Recent assessment performance indicates weaknesses in data manipulation and statistical analysis."
}
```

### Recommendation item
```json
{
  "title": "Introduction to SQL for Official Statistics",
  "provider": "IGOT",
  "is_mock": true,
  "competency_addressed": "SQL",
  "gap": 25,
  "relevance_score": 0.91,
  "estimated_effort_hours": 6,
  "reason": "Recommended because: (1) role requires SQL level ~80; (2) current score 55; (3) recent assessment 61%; (4) course targets SQL data analysis.",
  "url": "https://example.igot.mock/courses/sql-basics"
}
```

## 4. Authorization Matrix (MVP)

| Resource | LEARNER | ADMIN |
|----------|---------|-------|
| Own profile / gaps / assessments / recommendations | R/W | R/W |
| Other users | — | R/W |
| Competency framework mutate | — | R/W |
| Document upload & question gen | — | R/W |
| Audit logs | — | R |
| Assistant (own context) | R/W | R/W |

## 5. Versioning

MVP uses unversioned `/api`. Introduce `/api/v1` when external consumers appear.

---

*Document status: Phase 0.*
