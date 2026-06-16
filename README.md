# LitMatch

**Học văn học Việt Nam như chơi một trò chơi.** LitMatch turns Vietnamese
literature study into character discovery: swipe to meet literary characters,
chat with source-grounded AI personas, and climb a three-phase challenge that
*levels each character's portrait up* — card-game style — on the way to the
leaderboard. **Ten canonical characters** ship today (Chí Phèo, Mị, Xuân Tóc Đỏ,
Lục Vân Tiên, Thúy Kiều, Lão Hạc, Chị Dậu, Ông Sáu, Ông Hai, Vũ Nương).

---

## The experience

### 1 · Onboarding
Pick a display name and grade level, then step into the journey.

![Onboarding](docs/screenshots/01-onboarding.png)

### 2 · Discover
Swipe through a deck of literary characters rendered as aged-parchment, Đông Hồ /
Hàng Trống–style portraits. Swipe right to add a character to your collection and
unlock their chat.

![Discover deck](docs/screenshots/02-discover.png)

### 3 · Challenge
Each character has a **three-phase challenge** (4 multiple-choice + 1
rubric-graded open-ended question per phase). A numbered question-pip row and a
phase stepper keep you oriented; the open-ended answer is graded server-side
against a rubric using pgvector retrieval + an LLM.

![Challenge with phase stepper and question pips](docs/screenshots/03-challenge.png)

### 4 · Level up
Pass a phase and the character's portrait **brightens and ascends to its next
level** with a star-burst reveal and a chime — earning a parchment → gold → Tết-red
badge as the story deepens.

![Level-up reveal](docs/screenshots/04-levelup.png)

> Rounding out the loop: a **Collection** view that sorts characters by level
> with per-level badges, source-grounded **Chat**, and a **Leaderboard**.

---

## Run it locally

**Prerequisites:** Node 18+, Python 3.11+, Docker Desktop, and an OpenAI API key.

```sh
# 1. Env — put OPENAI_API_KEY in the repo-root .env (Vite + backend both read it)
cp .env.example .env

# 2. Frontend deps
cd frontend && npm install && cd ..

# 3. Backend deps
cd backend && python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt && cd ..

# 4. Postgres + schema + seed (characters, challenges, demo users)
docker compose up -d postgres          # wait until `docker compose ps postgres` is healthy
unset DEBUG                             # backend expects DEBUG to be a boolean
cd backend && ./.venv/bin/python scripts/seed_database.py && cd ..

# 5. Knowledge-base embeddings — restore the team's pre-embedded pgvector dump
#    (no OpenAI cost, ~1s): https://drive.google.com/file/d/1cGlRIXH9EOJEwfb22USsUhSV6NCAcq_D/view
bash scripts/restore-knowledge-chunks.sh
```

Then run the three processes (each from the project root):

```sh
docker compose up -d postgres                                   # database
cd backend && unset DEBUG && ./.venv/bin/python -m uvicorn main:app --reload --port 8081
cd frontend && npm run dev                                      # → http://localhost:5173
```

The frontend can also run **offline in mock mode** (no backend) for UI demos —
`VITE_REAL_ENDPOINTS` in the root `.env` whitelists which endpoints hit the real
backend (empty = all mock). FE state persists to `localStorage`; reset via
**Hồ sơ → Đặt lại dữ liệu thử nghiệm**.

<details>
<summary>Troubleshooting setup</summary>

- `npm ERR! enoent`: run npm from `frontend/`, or `npm --prefix frontend run dev`.
- `cd: no such file or directory: backend`: you're already inside `backend/`.
- `ConnectionResetError` while seeding: Postgres is still initializing — wait for
  `docker compose ps postgres` to show `healthy`, then rerun.
- `DEBUG Input should be a valid boolean`: `unset DEBUG` (or prefix `env DEBUG=false`).

</details>

---

## Under the hood

- **Frontend** — React 18 + TypeScript + Vite, Zustand, TanStack Query,
  react-tinder-card; Capacitor for iOS/Android packaging.
- **Backend** — FastAPI, async SQLAlchemy, Postgres + pgvector, OpenAI GPT-4o +
  `text-embedding-3-large`, SSE streaming for chat.
- **RAG** — per-character curated knowledge base embedded into `knowledge_chunks`;
  chat and open-ended grading retrieve real evidence (lexical fallback if vectors
  are unavailable).

```
frontend/   React + TS + Vite + Capacitor
backend/    FastAPI + Postgres + pgvector + OpenAI
docs/       API.md (backend contract) · DEPLOYMENT.md (Cloud Run, Android, env)
```

## More docs

- **[docs/API.md](docs/API.md)** — live backend API (endpoints, schemas, the
  open-ended grading contract).
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** — local, Cloud Run, Android APK,
  mobile testing, env reference, CI/CD.
- **[PRD.md](PRD.md)** — product spec.
