# LitMatch Backend API

This documents the **live** LitMatch backend (FastAPI + Postgres/pgvector +
OpenAI). It is no longer a forward-looking mock contract — the backend is
implemented and runs at `http://localhost:8081` in local dev.

> **Source of truth:** the code. Routes live in `backend/api/routes/`, wire
> schemas in `backend/models/schemas.py`, and the frontend types in
> `frontend/src/types/index.ts`. This doc is a human-readable map; when it
> disagrees with those files, the files win.

The frontend chooses mock vs. real per endpoint via the `VITE_REAL_ENDPOINTS`
whitelist (see `frontend/src/api/adapter.ts`). With no backend running you can
still demo the UI in mock mode; the deployed app talks to the real API below.

## 1. Conventions

- **Base URL:** `${VITE_API_BASE_URL}` (default `http://localhost:8081`), all
  routes under the `/api/v1` prefix.
- **Content type:** `application/json; charset=utf-8`, except `POST
  /chat/stream` which returns `text/event-stream` (see §4).
- **Encoding:** UTF-8 throughout; Vietnamese diacritics preserved exactly.
- **Auth:** OAuth/OIDC (Google) under `/api/v1/auth/*` with a signed HTTP-only
  session cookie. Gameplay endpoints also accept explicit `user_id` (UUID) for
  the pre-auth flow.
- **IDs:** Characters have both a stable kebab-case `slug` (`chi-pheo`) and a
  backend `UUID`. Endpoints that take `{character_id}`/`{user_id}` expect the
  UUID; `slug` is used for content/seed cross-references.
- **Time:** ISO 8601 UTC.

## 2. Error format

Non-2xx responses return a JSON error envelope; common cases:

| HTTP | When |
| --- | --- |
| 400 | Malformed body / answer-count mismatch |
| 401 | Auth required / invalid session |
| 403 | Character not matched (chat/challenge gated) |
| 404 | Unknown id |
| 500 | Server error |

## 3. Endpoints (prefix `/api/v1`)

### Auth — `backend/api/routes/auth.py`
- `GET  /auth/login/{provider}` — start OAuth (provider: `google`); `302` to the IdP, `503` if OAuth isn't configured.
- `GET  /auth/callback/{provider}` — OAuth redirect URI; sets the session and redirects to the safe `next` target.
- `GET  /auth/me` → `UserResponse` (`401` if no session).
- `POST /auth/logout` → `{ "ok": true }`.

### Users — `users.py`
- `POST /users` (`UserCreate`) → `UserResponse` — create the pre-auth user.
- `GET  /users/{user_id}` → `UserResponse`.
- `GET  /users/{user_id}/matches` → `MatchedCharactersResponse`.

### Deck & characters — `deck.py`, `characters.py`
- `GET /deck` → `DeckResponse` (`{ characters: CharacterCard[] }`). Returns the unswiped deck for the user.
- `GET /characters` → `CharacterCard[]` (full catalog; used by the Collection view).
- `GET /characters/{character_id}` → `CharacterDetail`.
- `GET /characters/{character_id}/relationships` → `CharacterRelationshipsResponse`.
- `GET /characters/{character_id}/events` → `CharacterEventsResponse`.

### Interactions — `interactions.py`
- `POST /interactions/swipe` (`SwipeRequest { user_id, character_id, direction }`) → `SwipeResponse`. A right swipe records a match (the FE also awards `+10` client-side for responsiveness).

### Chat — `chat.py`
- `GET  /chat/history?...` → `ChatHistoryResponse`.
- `POST /chat/stream` (`ChatRequest`) → **SSE** stream (see §4). Source-grounded reply in the character's voice via RAG over the curated knowledge base. `403` if the character isn't matched (returned as JSON, the SSE stream is not opened).

### Challenges — `challenges.py`
Two distinct systems coexist:

**A. Legacy single challenge (backend-graded).** One multiple-choice quiz per
character, scored on the server.
- `GET  /characters/{character_id}/challenge` → `ChallengeQuestionsResponse` — questions only; the correct-answer index is withheld.
- `POST /challenges/submit` (`ChallengeSubmission { user_id, character_id, answers: number[] }`) → `ChallengeResult`.
- `GET  /challenges/result?user_id=&character_id=` → `ChallengeAttemptResponse` — the stored attempt.

**B. Three-phase level challenges (frontend-seeded).** The leveling flow's 15
questions per character (3 phases × 5: 4 multiple-choice + 1 open-ended) live as
**frontend seed data** in `frontend/src/data/levelChallenges.ts`. Multiple-choice
answers are scored client-side (`frontend/src/lib/scoring.ts`); only the
open-ended question of each phase is graded by the backend:
- `POST /challenges/grade-open-ended` (`OpenEndedGradeSubmission`) → `OpenEndedGradeResult`. The FE sends the question + rubric; the grader runs pgvector retrieval over the character's knowledge base plus an LLM rubric check, falling back to lexical retrieval if vectors are unavailable.

### Leaderboard — `leaderboard.py`
- `GET /leaderboard` → `LeaderboardResponse` (`{ entries: LeaderboardEntry[] }`), descending by points.

### Admin — `admin.py`
- `GET /admin/rag/diagnostics` → `RagDiagnosticsResponse`.
- `GET /admin/debug/config` — non-secret runtime config snapshot.

## 4. Chat streaming (SSE)

`POST /chat/stream` returns `text/event-stream`. Event types:

| Event | Schema | Meaning |
| --- | --- | --- |
| `token` | `{ "text": string }` | A chunk of the reply; FE appends in order. |
| `source` | `{ "id", "title", "snippet" }` | A retrieved citation (optional, any time). |
| `error` | `{ "code", "message" }` | Stream-level error; FE stops and shows it. |
| `done`  | `{ "messageId": string }` | Final event; stream closes. |

The full reply is the in-order concatenation of `token.text`. Behind nginx, set
`Cache-Control: no-cache` and `X-Accel-Buffering: no`. The backend aborts
generation if the client disconnects. Guardrails: admit uncertainty when
sources are thin, separate interpretation from cited fact, and refuse full
canned essays (offer outline/evidence help instead).

## 5. Key wire schemas

Authoritative definitions are in `backend/models/schemas.py`. The two that the
leveling work added:

```python
# Request to POST /challenges/grade-open-ended
class OpenEndedGradeSubmission:
    character_slug: str
    character_name: str
    work_title:  str | None
    phase_title: str | None
    question: str          # the open-ended prompt
    answer:   str          # the player's free-text answer
    rubric:   str          # "Đạt nếu nêu được: ..." criteria
    evidence: str | None

# Response
class OpenEndedGradeResult:
    score: int             # 0 or 1
    passed: bool
    feedback: str
    matched_criteria:  list[str]
    missing_criteria:  list[str]
    confidence: float      # 0..1
    retrieval_mode: str    # "vector" | "lexical"
    sources: list[dict]
```

`ChallengeResult` (legacy submit): `{ score, total, passed, points_earned,
explanations: string[], correct_answers: number[] }`.

## 6. Content seed

The backend seeds **ten** characters (`backend/scripts/seed_database.py`),
matched to the frontend slugs:

| Slug | Character | Work / Author |
| --- | --- | --- |
| `chi-pheo` | Chí Phèo | Chí Phèo — Nam Cao |
| `mi` | Mị | Vợ chồng A Phủ — Tô Hoài |
| `xuan-toc-do` | Xuân Tóc Đỏ | Số đỏ — Vũ Trọng Phụng |
| `luc-van-tien` | Lục Vân Tiên | Lục Vân Tiên — Nguyễn Đình Chiểu |
| `thuy-kieu` | Thúy Kiều | Truyện Kiều — Nguyễn Du |
| `lao-hac` | Lão Hạc | Lão Hạc — Nam Cao |
| `chi-dau` | Chị Dậu | Tắt đèn — Ngô Tất Tố |
| `ong-sau` | Ông Sáu | Chiếc lược ngà — Nguyễn Quang Sáng |
| `ong-hai` | Ông Hai | Làng — Kim Lân |
| `vu-nuong` | Vũ Nương | Chuyện người con gái Nam Xương — Nguyễn Dữ |

Per-character rich seed (bio, voice, conflict, level images, legacy challenge)
is in `frontend/src/data/characters.ts`; the 3-phase level challenges are in
`frontend/src/data/levelChallenges.ts`; the RAG knowledge base is under
`backend/knowledge_base/` (embedded into `knowledge_chunks`).

## 7. Open questions

1. **Auth enforcement:** sessions exist but gameplay endpoints still accept explicit `user_id`; decide when to switch fully to session identity.
2. **Level-challenge persistence:** level progress is currently client-side (`localStorage`, Zustand). If it should sync server-side, the level challenges and per-phase results need a backend home.
3. **Open-ended grading cost/limits:** each open-ended submission is a real OpenAI call; no throttle today.
