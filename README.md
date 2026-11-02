# Job Queue Lab

Backend-focused lab: **enqueue jobs over HTTP → Redis list → worker process → SQLite status**, with a small **React/Vite** UI that polls for updates.

## Architecture

```text
React (:5173)  --POST/GET /jobs-->  FastAPI (:8000)  --LPUSH-->  Redis
                                         |                         |
                                      SQLite                   BRPOP worker
```

Job lifecycle: `queued` → `running` → `succeeded` | `failed` (retries up to `max_attempts`). Cancel only while `queued`.

### Job types

| Type | Payload | Behavior |
|------|---------|----------|
| `sleep` | `{ "seconds": 1-10 }` | Sleep, return `{ "slept": n }` |
| `http_fetch` | `{ "url": "..." }` | GET URL; store status code + body length |
| `fail` | `{ "message": "..." }` | Always fail (good for retry demos) |

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for Redis), or any Redis on `localhost:6379`

## Quick start

```bash
# 1) Redis
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

## Try this

1. Submit a `sleep` job (2s) → watch `queued` → `running` → `succeeded`.
2. Submit the same question again while watching Redis: the worker uses `BRPOP`.
3. Submit `fail` → see retries (`attempts` climb) then `failed`.
4. Submit `http_fetch` with `https://httpbin.org/get` → inspect result JSON in the detail panel.
5. Enqueue a long `sleep`, click the row while `queued`, hit **Cancel**.

## Layout

```text
app/                 FastAPI API, SQLite models, Redis queue, worker
web/                 React + Vite + TypeScript UI
docker-compose.yml   Redis
```

## Learning checklist

- [ ] API and worker are **separate processes**
- [ ] Redis holds **job ids**, SQLite holds **durable status/results**
- [ ] Failed jobs re-queue until `max_attempts`
- [ ] React polls while any job is `queued` / `running`
- [ ] Vite proxy + FastAPI CORS keep FE and BE on different ports
