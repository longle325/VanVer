# Vanver — Deployment Guide

Complete guide for running, building, and deploying Vanver across all targets:
local development, Cloud Run (GCP), and Android APK.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Local Development](#2-local-development)
3. [Frontend ↔ Backend Connection](#3-frontend--backend-connection)
4. [Cloud Run Deployment (GCP)](#4-cloud-run-deployment-gcp)
5. [Android APK Build](#5-android-apk-build)
6. [Mobile Testing](#6-mobile-testing)
7. [Environment Variables Reference](#7-environment-variables-reference)
8. [CI/CD Workflows](#8-cicd-workflows)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Project Structure

```
Vanver/
├── frontend/                    # React 18 + TypeScript + Vite + Capacitor
│   ├── src/
│   │   ├── api/
│   │   │   ├── adapter.ts       # Routes each endpoint to mock or real client
│   │   │   ├── mockClient.ts    # Local seed data (works offline)
│   │   │   ├── realClient.ts    # HTTP + SSE streaming to backend
│   │   │   ├── sse.ts           # Server-Sent Events parser
│   │   │   └── queries.ts       # TanStack Query hooks
│   │   ├── components/          # Shared UI (AppShell, CharacterCard, etc.)
│   │   ├── routes/              # Page screens (Discover, Chat, Challenge, etc.)
│   │   ├── stores/useAppStore.ts  # Zustand state + localStorage/Capacitor persistence
│   │   └── styles/              # Folk Woodblock theme CSS
│   ├── public/
│   │   ├── characters/          # Character portrait PNGs
│   │   ├── voices/              # Character voice WAV files
│   │   └── fonts/               # Self-hosted Be Vietnam Pro + Noto Serif
│   ├── android/                 # Capacitor Android project
│   ├── ios/                     # Capacitor iOS project
│   ├── Dockerfile               # Multi-stage: Node build + nginx serve
│   ├── nginx.conf               # SPA routing + static asset caching
│   └── capacitor.config.ts      # Capacitor native config
│
├── backend/                     # FastAPI + PostgreSQL + pgvector
│   ├── api/routes/              # REST endpoints
│   ├── services/                # Chat, RAG retriever, Codex agent
│   ├── models/                  # SQLAlchemy ORM + Pydantic schemas
│   ├── knowledge_base/          # Literary texts, embeddings, manifest
│   ├── scripts/                 # Seed DB, embed knowledge, extract PDFs
│   ├── migrations/              # Alembic schema versions
│   └── requirements.txt
│
├── .github/workflows/
│   ├── build-android.yml        # Build APK on push to deploy
│   └── deploy-cloudrun.yml      # Deploy frontend to Cloud Run on push to deploy
│
└── docs/
    ├── API.md                   # Backend API contract (385 lines)
    └── DEPLOYMENT.md            # This file
```

---

## 2. Local Development

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 22+ | Frontend build, Capacitor CLI |
| Python | 3.11+ | Backend |
| Docker | latest | PostgreSQL + pgvector |
| OpenAI API key | — | Chat + embeddings |

### Quick start (frontend only, no backend needed)

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

The frontend works fully offline using mock data. All 5 characters, challenges,
leaderboard, and chat (mock replies) work without the backend.

### Full stack (frontend + backend)

```bash
# Terminal 1 — Database
docker compose up -d postgres

# Terminal 2 — Backend
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python scripts/seed_database.py
./.venv/bin/python -m uvicorn main:app --reload --port 8081

# Terminal 3 — Frontend
cd frontend
npm run dev
# Open http://localhost:5173
```

### Restore knowledge-base embeddings (optional, for RAG chat)

Instead of re-embedding all literary texts ($$$), restore the team's pre-built
pgvector dump:

```bash
# Download from: https://drive.google.com/file/d/1cGlRIXH9EOJEwfb22USsUhSV6NCAcq_D
bash scripts/restore-knowledge-chunks.sh
```

---

## 3. Frontend ↔ Backend Connection

The frontend has a **per-endpoint mock/real router** (`src/api/adapter.ts`).
The mock client is the offline fallback; the project ships a **repo-root**
`.env` that points the app at the real backend. Vite reads that repo-root
`.env` (`envDir: ".."` in `frontend/vite.config.ts`), so set these there — not
in `frontend/.env`:

```bash
# Backend URL (Vite proxy handles this in dev, needed for production)
VITE_API_BASE_URL=http://localhost:8081/api/v1

# Which endpoints hit the real backend (empty = all mock)
# Options: auth, characters, deck, match, challenge, leaderboard, chat
VITE_REAL_ENDPOINTS=all
```

### Granular control

You can wire endpoints individually while keeping the rest mocked:

```bash
# Only auth and chat hit the real backend; everything else is mock
VITE_REAL_ENDPOINTS=auth,chat
```

This is useful for:
- Testing a specific backend feature without seeding everything
- Running demos when the backend is partially ready
- Debugging a single endpoint in isolation

### How the proxy works (dev)

In development, the Vite dev server proxies `/api/*` to the backend:

```
Browser :5173  →  Vite dev server  →  /api/*  →  FastAPI :8081
```

This is configured in `frontend/vite.config.ts`:

```ts
proxy: {
  "/api": {
    target: "http://localhost:8081",
    changeOrigin: true,
  },
}
```

No CORS issues in dev because the browser sees everything on `:5173`.

### CORS in production / Capacitor

The backend allows these origins (`backend/core/config.py`):

| Origin | Context |
|--------|---------|
| `http://localhost:5173` | Vite dev server |
| `http://127.0.0.1:5173` | Vite dev server (alt) |
| `http://localhost:3000` | Alternative dev port |
| `capacitor://localhost` | iOS Capacitor WebView |
| `https://localhost` | Android Capacitor WebView |

---

## 4. Cloud Run Deployment (GCP)

### Architecture

```
GitHub push to deploy
        │
        ▼
GitHub Actions workflow
        │
        ├── Build Docker image (Node 22 + nginx)
        ├── Push to Artifact Registry (us-central1)
        └── Deploy to Cloud Run
                │
                ▼
        https://vanver-frontend-xxxxx.run.app
```

The default deployment region is `us-central1` to stay on Cloud Run Tier 1
pricing and make best use of free-tier credits. Use `asia-southeast1` only when
Singapore latency is worth the higher Tier 2 pricing.

### One-time GCP setup

#### 4.1 Create service account

```bash
PROJECT_ID=your-gcp-project-id

gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions Deployer" \
  --project=$PROJECT_ID
```

#### 4.2 Grant permissions

```bash
SA=github-deployer@${PROJECT_ID}.iam.gserviceaccount.com

# Push images to Artifact Registry
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/artifactregistry.writer"

# Deploy to Cloud Run
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/run.admin"

# Act as itself when deploying
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/iam.serviceAccountUser"
```

#### 4.3 Allow GitHub to impersonate the service account

```bash
gcloud iam service-accounts add-iam-policy-binding $SA \
  --project=$PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/724238746267/locations/global/workloadIdentityPools/github-actions/attribute.repository/longle325/Vanver"
```

#### 4.4 Create Artifact Registry repository

```bash
gcloud artifacts repositories create vanver \
  --repository-format=docker \
  --location=us-central1 \
  --project=$PROJECT_ID
```

Apply the cleanup policy so per-deploy images do not accumulate indefinitely:

```bash
gcloud artifacts repositories set-cleanup-policies vanver \
  --project=$PROJECT_ID \
  --location=us-central1 \
  --policy=.github/artifact-registry-cleanup-policy.json
```

The policy deletes images older than 14 days while keeping the 5 most recent
versions of each package.

#### 4.5 Set GitHub repository variables

Go to **Settings → Secrets and variables → Actions → Variables** and add:

| Variable name | Value |
|---------------|-------|
| `GCP_PROJECT_ID` | your-gcp-project-id |
| `GCP_SERVICE_ACCOUNT` | github-deployer@your-gcp-project-id.iam.gserviceaccount.com |

### Deploy

Push to the `deploy` branch:

```bash
git push origin your-branch:deploy
```

The workflow runs automatically. When done, the deployed URL appears in the
GitHub Actions job summary.

### Manual deploy (without CI)

```bash
cd frontend

# Build and push
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/vanver/vanver-frontend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/vanver/vanver-frontend:latest

# Deploy
gcloud run deploy vanver-frontend \
  --project $PROJECT_ID \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/vanver/vanver-frontend:latest \
  --region us-central1 \
  --port 8080 \
  --allow-unauthenticated
```

### Cloud Run config

| Setting | Value | Rationale |
|---------|-------|-----------|
| Port | 8080 | nginx default in container |
| Memory | 256Mi | Static files, no server processing |
| CPU | 1 | Sufficient for nginx |
| Min instances | 0 | Scale to zero when idle (free tier) |
| Max instances | 3 | Limit costs |
| Auth | unauthenticated | Public frontend |

---

## 5. Android APK Build

### Via CI (recommended)

Push to `deploy` branch → GitHub Actions builds the APK automatically.

Download: **GitHub → Actions → latest run → Artifacts → `vanver-debug-apk`**

### Via CLI (local)

Prerequisites: JDK 21, Android SDK (platforms;android-36, build-tools;36.0.0)

```bash
cd frontend

# Build web → sync to Capacitor → assemble APK
npm run cap:android:build

# APK output:
# frontend/android/app/build/outputs/apk/debug/app-debug.apk
```

### Install on device

```bash
# Via USB (with ADB)
adb install -r android/app/build/outputs/apk/debug/app-debug.apk

# Or transfer the .apk file manually and tap to install
# (enable "Install from unknown sources" in phone Settings)
```

### Android SDK CLI setup (no Android Studio)

```bash
# Download command-line tools
mkdir -p ~/android-sdk/cmdline-tools
cd ~/android-sdk/cmdline-tools
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-11076708_latest.zip
mv cmdline-tools latest

# Add to ~/.bashrc
export ANDROID_HOME=~/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Install SDK packages
source ~/.bashrc
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-36" "build-tools;36.0.0"

# Tell Gradle where the SDK is
echo "sdk.dir=$HOME/android-sdk" > frontend/android/local.properties
```

---

## 6. Mobile Testing

### Option A — Same WiFi (quickest)

```bash
cd frontend
npm run dev -- --host
# Open the "Network" URL on your phone's browser
```

### Option B — Ngrok (remote access)

```bash
# Terminal 1
cd frontend && npm run dev -- --host

# Terminal 2
ngrok http 5173
# Open the ngrok URL on any phone
```

### Option C — Capacitor native app

```bash
# Android (CLI)
cd frontend && npm run cap:android:build
# Transfer APK to phone

# iOS (requires Mac + Xcode)
cd frontend && npm run cap:ios
```

### Option D — Capacitor live reload (edit code, see changes on device)

```bash
# Edit capacitor.config.ts, uncomment server.url with your IP:
#   server: { url: "http://192.168.x.x:5173", cleartext: true }

cd frontend
npm run dev -- --host
npx cap run android --livereload --external
```

---

## 7. Environment Variables Reference

### Root `.env` (shared by frontend + backend)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/vanver

# OpenAI
OPENAI_API_KEY=sk-your-key-here
CHAT_MODEL=gpt-5-mini
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSIONS=3072

# Knowledge retrieval
KNOWLEDGE_BASE_DIR=./knowledge_base
RAG_TOP_K=5
RAG_MIN_SIMILARITY=0.0

# OAuth / backend session
SESSION_SECRET_KEY=replace-with-a-long-random-secret
SESSION_COOKIE_NAME=litmatch_session
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=lax
SESSION_MAX_AGE_SECONDS=1209600
OAUTH_POST_LOGIN_REDIRECT=http://localhost:5173
OAUTH_ALLOWED_REDIRECT_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","capacitor://localhost","https://localhost"]
OAUTH_CALLBACK_BASE_URL=http://localhost:8081
OAUTH_GOOGLE_CLIENT_ID=your-google-client-id
OAUTH_GOOGLE_CLIENT_SECRET=your-google-client-secret
OAUTH_GOOGLE_SERVER_METADATA_URL=https://accounts.google.com/.well-known/openid-configuration
OAUTH_GOOGLE_SCOPE=openid email profile

# Frontend (VITE_ prefix required for Vite to expose to client)
VITE_API_BASE_URL=http://localhost:8081/api/v1
VITE_REAL_ENDPOINTS=all
```

### Frontend-only vars

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8081/api/v1` | Backend API base URL |
| `VITE_REAL_ENDPOINTS` | _(empty = all mock)_ | Comma-separated: `auth,characters,deck,match,challenge,leaderboard,chat` or `all` |

### Backend-only vars

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `OPENAI_API_KEY` | — | Required for chat + embeddings |
| `CHAT_MODEL` | `gpt-4o` | Model for character chat responses |
| `CODEX_MODEL` | `codex-mini` | Model for Codex knowledge search |
| `EMBEDDING_MODEL` | `text-embedding-3-large` | Model for RAG embeddings |
| `EMBEDDING_DIMENSIONS` | `3072` | Embedding vector size |
| `RAG_TOP_K` | `5` | Number of RAG chunks to retrieve |
| `RAG_MIN_SIMILARITY` | `0.0` | Minimum cosine similarity threshold |
| `SESSION_SECRET_KEY` | — | Required for OAuth login session signing |
| `SESSION_COOKIE_NAME` | `litmatch_session` | Browser cookie name for the backend session |
| `SESSION_COOKIE_SECURE` | `false` | Set `true` behind HTTPS in production |
| `SESSION_COOKIE_SAMESITE` | `lax` | SameSite policy for the backend session cookie |
| `SESSION_MAX_AGE_SECONDS` | `1209600` | Session cookie lifetime in seconds |
| `OAUTH_POST_LOGIN_REDIRECT` | `http://localhost:5173` | Default safe redirect after login |
| `OAUTH_ALLOWED_REDIRECT_ORIGINS` | local dev origins | Allowed absolute `next` URL origins |
| `OAUTH_CALLBACK_BASE_URL` | request host | Public backend origin used for OAuth callback URLs |
| `OAUTH_GOOGLE_CLIENT_ID` | — | Google OAuth client ID |
| `OAUTH_GOOGLE_CLIENT_SECRET` | — | Google OAuth client secret |
| `OAUTH_GOOGLE_SERVER_METADATA_URL` | Google OpenID metadata URL | OpenID provider discovery URL |
| `OAUTH_GOOGLE_SCOPE` | `openid email profile` | Requested Google OAuth scopes |
| `DEBUG` | `false` | Enable debug logging |

### GitHub Actions variables (repo settings)

| Variable | Where | Purpose |
|----------|-------|---------|
| `GCP_PROJECT_ID` | Repo → Settings → Variables | Google Cloud project ID |
| `GCP_SERVICE_ACCOUNT` | Repo → Settings → Variables | Service account email for deployment |

---

## 8. CI/CD Workflows

Both workflows trigger on push to the `deploy` branch.

### `build-android.yml` — Android APK

```
Checkout → Node 22 → JDK 21 → Android SDK
→ npm ci → vite build → cap sync → gradlew assembleDebug
→ Upload artifact (30-day retention)
```

Download: GitHub → Actions → run → Artifacts → `vanver-debug-apk`

### `deploy-cloudrun.yml` — Cloud Run

```
Checkout → GCP Auth (Workload Identity Federation)
→ Docker build → Push to Artifact Registry
→ gcloud run deploy → Output URL in job summary
```

### Triggering a deploy

```bash
# From any branch, push to deploy without switching
git push origin your-branch:deploy
```

---

## 9. Troubleshooting

### Frontend shows mock data instead of real backend

- Check `frontend/.env` has `VITE_REAL_ENDPOINTS=all`
- Restart the Vite dev server after changing `.env`
- Verify backend is running: `curl http://localhost:8081/health`

### CORS errors in browser console

- Backend CORS config is in `backend/core/config.py`
- Ensure the origin matches exactly (http vs https, port number)
- In dev, the Vite proxy should bypass CORS entirely

### Android APK build fails with "JAVA_COMPILER not found"

- You need JDK 21 (not JRE): `sudo apt install msopenjdk-21`
- Verify: `javac -version` should print `javac 21.x.x`

### Capacitor CLI requires Node >= 22

- Update Node: `nvm install 22 && nvm use 22`
- The CI workflow uses `node-version: 22`

### Cloud Run deploy fails with "permission denied"

- Ensure the service account has `roles/run.admin`, `roles/artifactregistry.writer`, `roles/iam.serviceAccountUser`
- Ensure Workload Identity Federation allows the GitHub repo (check the `attribute.repository` condition)
- Ensure `GCP_PROJECT_ID` and `GCP_SERVICE_ACCOUNT` are set in GitHub repo variables (not secrets)

### Chat doesn't stream / shows error

- Check `OPENAI_API_KEY` is set in backend `.env`
- Check the backend logs: `uvicorn` terminal should show SSE chunks
- Try `VITE_REAL_ENDPOINTS=chat` to test chat alone with mock data for everything else

### Knowledge base returns empty results

- Run `python scripts/seed_database.py` to seed characters
- Restore embeddings: `bash scripts/restore-knowledge-chunks.sh`
- Check `RAG_MIN_SIMILARITY` — set to `0.0` to disable threshold filtering
