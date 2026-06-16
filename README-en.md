# Vanver

> Đọc bản tiếng Việt tại [README.md](README.md).

You close the book.You sigh.

It has been two hours, and somehow the plot of tomorrow’s literature text is still refusing to stay in your brain. The character analysis sounds like something written by a committee of very tired adults.

And the worst part? The story probably *is* interesting.It just doesn’t feel that way when you’re forced to memorize it like a grocery list.

But literature does not have to be a test of who can suffer through the driest summary. What if you could meet literary characters as actual people — messy, wounded, funny, proud, stubborn, romantic, tragic people with rich inner lives?

Would you be more curious about Chí Phèo if you could talk to him?   
Would you pay more attention if discovering characters felt a little like swiping through profiles?

Be honest. Your eyes are wide open when it is Tinder. Literature deserves that kind of energy too.

**Meet Vanver.**

**Vanver helps you learn Vietnamese Literature like a game.**  
Instead of treating characters as things to memorize, Vanver turns them into people you can discover, collect, chat with, and level up.

Swipe to meet literary characters, talk to source-grounded AI personas, and take on a three-phase challenge that slowly reveals each character’s deeper portrait. The more you understand them, the more their world opens up.

**Ten iconic characters are waiting for you:**  
Chí Phèo, Mị, Xuân Tóc Đỏ, Lục Vân Tiên, Thúy Kiều, Lão Hạc, Chị Dậu, Ông Sáu, Ông Hai, and Vũ Nương.

---

## The experience

### 1 · Onboarding

Start simple: sign in with Google, then step into the story.

No heavy setup. No intimidating dashboard. Just you, your literature journey, and a cast of characters who are much more interesting than their exam summaries make them seem.

![Onboarding](docs/screenshots/01-onboarding.png)

### 2 · Discover

Swipe through a deck of Vietnamese literary characters, each reimagined as an aged-parchment portrait inspired by Đông Hồ and Hàng Trống folk art.Swipe right to add a character to your collection and unlock their chat.

Yes, it is a little like character Tinder. Except instead of “looking for something casual,” they are carrying generational trauma, moral conflict, and several pages of literary significance.

![Discover deck](docs/screenshots/02-discover.png)

### 3 · Challenge

Each character comes with a **three-phase challenge**.

Every phase includes:

- 4 multiple-choice questions
- 1 open-ended question graded against a rubric

The numbered question pips help you keep track of where you are, while the phase stepper shows how far you have come.

For open-ended answers, the backend grades your response using pgvector retrieval and an LLM, so your answer is checked against real textual evidence instead of vague “sounds good enough” guessing.

![Challenge with phase stepper and question pips](docs/screenshots/03-challenge.png)

### 4 · Level up

Pass a phase, and your character’s portrait evolves.

The image brightens, the character ascends to the next level, and you get a star-burst reveal with a chime. Each level moves the badge from parchment → gold → Tết-red, marking how much deeper your understanding has become.

Basically: character analysis, but with dopamine.

![Level-up reveal](docs/screenshots/04-levelup.png)

To complete the loop, Vanver also includes a **Collection** view that sorts characters by level, per-level badges, source-grounded **Chat**, and a **Leaderboard** for a little friendly academic chaos.

---

## Run it locally

**Prerequisites:** Node 18+, Python 3.11+, Docker Desktop, and an OpenAI API key.

```sh
# 1. Env — put OPENAI_API_KEY in the repo-root .env
# Vite + backend both read it
cp .env.example .env

# 2. Frontend deps
cd frontend && npm install && cd ..

# 3. Backend deps
cd backend && python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt && cd ..

# 4. Postgres + schema + seed
# This seeds characters, challenges, and demo users
docker compose up -d postgres          # wait until `docker compose ps postgres` is healthy
unset DEBUG                             # backend expects DEBUG to be a boolean
cd backend && ./.venv/bin/python scripts/seed_database.py && cd ..

# 5. Knowledge-base embeddings
# Restore the team's pre-embedded pgvector dump
# No OpenAI cost, usually takes ~1s:
# https://drive.google.com/file/d/1cGlRIXH9EOJEwfb22USsUhSV6NCAcq_D/view
bash scripts/restore-knowledge-chunks.sh
```

Then run the three processes below, each from the project root:

```sh
docker compose up -d postgres                                   # database
cd backend && unset DEBUG && ./.venv/bin/python -m uvicorn main:app --reload --port 8081
cd frontend && npm run dev                                      # → http://localhost:5173
```

The frontend can also run **offline in mock mode**, which is useful when you just want to demo the UI without starting the backend.

In the root `.env` file, `VITE_REAL_ENDPOINTS` controls which endpoints call the real backend. Leave it empty and everything will use mock data.

Frontend state is saved in `localStorage`. To reset the demo data, go to:

**Hồ sơ → Đặt lại dữ liệu thử nghiệm**

<details>
<summary>Troubleshooting setup</summary>

- `npm ERR! enoent`: you are probably running npm from the wrong folder. Run it from `frontend/`, or use `npm --prefix frontend run dev`.
- `cd: no such file or directory: backend`: you are probably already inside the `backend/` folder.
- `ConnectionResetError` while seeding: Postgres is still waking up. Wait until `docker compose ps postgres` shows `healthy`, then run the seed command again.
- `DEBUG Input should be a valid boolean`: run `unset DEBUG`, or prefix the command with `env DEBUG=false`.

</details>

---

## Under the hood

- **Frontend** — React 18 + TypeScript + Vite, Zustand, TanStack Query, and react-tinder-card. Capacitor is used for iOS/Android packaging.
- **Backend** — FastAPI, async SQLAlchemy, Postgres + pgvector, OpenAI GPT-4o + `text-embedding-3-large`, with SSE streaming for chat.
- **RAG** — each character has a curated knowledge base embedded into `knowledge_chunks`. Chat and open-ended grading retrieve real supporting evidence, with lexical search as a fallback if vector search is unavailable.

```txt
frontend/   React + TS + Vite + Capacitor
backend/    FastAPI + Postgres + pgvector + OpenAI
docs/       API.md backend contract · DEPLOYMENT.md Cloud Run, Android, env
```

## More docs

- **[docs/API.md](docs/API.md)** — current backend API, including endpoints, schemas, and the open-ended grading contract.
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** — local setup, Cloud Run, Android APK, mobile testing, env reference, and CI/CD.
- **[PRD.md](PRD.md)** — product spec.
