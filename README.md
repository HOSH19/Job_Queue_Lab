# Job Queue Lab

Backend-focused lab: **enqueue jobs over HTTP → Redis list → worker process → PostgreSQL status**, with a small **React/Vite** UI that polls for updates.

## Job types

| Type | Payload | Behavior |
|------|---------|----------|
| `sleep` | `{ "seconds": 1-10 }` | Sleep, return `{ "slept": n }` |
| `http_fetch` | `{ "url": "..." }` | GET URL; store status code + body length |
| `fail` | `{ "message": "..." }` | Always fail (good for retry demos) |

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for Redis + PostgreSQL)

## Quick start

```bash
# 1) Redis + PostgreSQL
docker compose up -d

# 2) API
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows; or: cp .env.example .env

# from repo root
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3) Worker (second terminal, same venv + repo root)
python -m app.worker

# 4) UI (third terminal)
cd web
npm install
npm run dev
```

Open http://localhost:5173 — Vite proxies `/jobs` and `/health` to the API.

API docs: http://localhost:8000/docs

Concept notes: [FastAPI](notes/01_fastapi.md) · [Redis](notes/02_redis_queue.md) · [Worker](notes/03_worker.md) · [PostgreSQL](notes/04_postgresql.md) · [Handlers](notes/05_job_handlers.md) · [React/Vite](notes/06_react_vite.md) · [HTTP](notes/07_http_methods.md) · [CORS](notes/08_cors.md) · [Polling](notes/09_polling_websockets.md) — index in [`notes/`](notes/).
