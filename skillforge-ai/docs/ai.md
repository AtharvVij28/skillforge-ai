# SkillForge AI — AI Architecture (Phase 0)

## 1. Goals

- Source-grounded question generation from uploaded materials
- Explainable skill-gap and recommendation narratives
- Grounded AI assistant answers tied to system state + documents
- **Provider-swappable** LLM and embedding layers (no vendor lock-in in code)

## 2. Abstraction Layers

```
┌──────────────────────────────────────────────┐
│ Application Services                         │
│  QuestionGenerationService                   │
│  AssistantService                            │
│  ExplanationService (templates + LLM polish) │
└─────────────────┬────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────┐
│ AI Facades                                   │
│  LLMProvider (interface)                     │
│  EmbeddingProvider (interface)               │
│  VectorStore (interface)                     │
└─────────────────┬────────────────────────────┘
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
 MockLLM     OpenAIAdapter  OtherAdapter
 MockEmbed   LocalEmbed     ...
 InMemoryVector / PGVector / Chroma (later)
```

### Interfaces (conceptual)

```python
class LLMProvider(Protocol):
    def generate(self, prompt: str, *, temperature: float, max_tokens: int) -> str: ...

class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...

class VectorStore(Protocol):
    def upsert(self, ids, vectors, metadata): ...
    def similarity_search(self, vector, k, filters) -> list[ChunkHit]: ...
```

Configuration selects implementations via env (`AI_PROVIDER=mock|openai|...`).

## 3. Document → Question Pipeline

```
UPLOAD (validate type/size)
  → EXTRACT (PDF/DOCX/TXT)
  → CLEAN (normalize whitespace, strip noise)
  → CHUNK (overlap, preserve page/section metadata)
  → STORE chunks + metadata in DB
  → EMBED chunks → VectorStore (or lexical fallback in MVP)
  → RETRIEVE candidate passages for target competency/topic
  → GENERATE MCQs with mandatory evidence quote
  → VALIDATE (evidence substring / entailment heuristic)
  → SAVE only questions that pass grounding checks
```

### Grounding rules (hard)

1. Every generated question must include `source_chunk_id` and `source_excerpt`.
2. If retrieved evidence is insufficient (below similarity threshold or too short), **skip** generation for that chunk.
3. Correct answer must be supportable from the excerpt; distractors must not invent unsupported facts.
4. Admin review flag `is_approved` before publish into learner assessments (recommended MVP gate).

### Question validation checks

- JSON schema valid (stem, 4 options, one correct key)
- Excerpt length ≥ minimum chars
- Stem keywords overlap with excerpt (simple lexical check)
- Optional LLM self-critique pass: “Is answer entailed by excerpt? yes/no”

## 4. Skill Gap Engine (deterministic + explainable)

Primary scoring is **rule-based**, not opaque LLM scoring:

```
gap = required_score - current_score
priority = f(gap, relevance_weight, department_priority)
confidence = f(assessment_recency, attempt_count, profile_completeness)
explanation = template filled with measurable inputs
```

LLM may optionally rephrase explanations; raw factors remain stored for audit.

## 5. Recommendation Engine

```
inputs: gaps, role requirements, learning history, career goals, assessment weaknesses
  → filter catalog via CourseProvider adapters (mock IGOT/NSSTA)
  → score relevance = weighted(gap, competency match, novelty, effort)
  → attach reason template
  → persist recommendations
```

Providers:

```
CourseProvider (ABC)
├── MockIGOTProvider
└── MockNSSTAProvider
```

Real HTTP adapters plug in later without changing the recommendation service.

## 6. Adaptive Learning Loop

On assessment submit:

1. Map question competencies → per-competency % correct  
2. Update `user_competencies.current_score` with bounded blend  
   e.g. `new = (1-α)*old + α*assessment_score` (α higher when confidence was low)  
3. Recompute gaps  
4. Regenerate / re-rank recommendations  
5. Emit audit events + dashboard deltas  

## 7. AI Assistant

### Grounding sources (priority order)

1. User profile, competencies, gaps, recommendations (structured DB)  
2. Recent assessment results  
3. Retrieved document chunks (if query is content-related)  
4. Competency framework definitions  

### Response policy

- Prefer citing structured facts (“Your Python score is 52; required is 80”)  
- If data missing: say so; do not invent scores or courses  
- Label mock catalog items as mock when relevant  

### MVP mode without live LLM

`MockLLMProvider` returns template answers assembled from DB facts so the demo works offline.

## 8. Configuration (env)

```
AI_PROVIDER=mock
LLM_API_KEY=
LLM_MODEL=
EMBEDDING_PROVIDER=mock
VECTOR_STORE=memory
AI_MAX_UPLOAD_MB=10
AI_CHUNK_SIZE=800
AI_CHUNK_OVERLAP=100
AI_MIN_EVIDENCE_CHARS=80
```

## 9. Risks Specific to AI

| Risk | Mitigation |
|------|------------|
| Hallucinated MCQs | Hard grounding + validation gate |
| Cost / latency | Batch generation; mock provider for CI |
| Embedding lock-in | VectorStore interface |
| Over-trust in LLM explanations | Store deterministic factors alongside prose |

---

*Document status: Phase 0.*
