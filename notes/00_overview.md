# Overview — what this lab is

You are building a **background job system**: the API accepts work quickly, Redis holds “to-do” ids, a separate **worker** process does the slow part, and **PostgreSQL** stores durable status the UI can show.

## Processes you run

| Process | Command | Role |
|---------|---------|------|
| Postgres + Redis | `make up` | Data store + queue |
| API | `make api` | HTTP + WebSocket |
| Worker | `make worker` | Claims jobs, runs handlers |
| UI | `make web` | Enqueue + watch status |

Health: `GET /health` should show Redis + DB `up`.

## Happy path (one sleep job)

1. UI `POST /jobs` with `{ "type": "sleep", "payload": { "seconds": 2 } }`.
2. API writes a row (`queued`) in Postgres and `ZADD`s the id into Redis.
3. Worker `BZPOPMIN`s the id, sets `running`, sleeps, sets `succeeded` + result JSON.
4. UI hears a WebSocket event (or polls) and refreshes the table.

## Failure path

`fail` jobs raise on purpose. Worker retries until `max_attempts`, then status becomes **`dead`** and the id goes to the **DLQ** (`GET /dlq`).

## Where to read next

| If you want… | Open |
|--------------|------|
| Core HTTP API | [01_fastapi.md](01_fastapi.md) |
| How Redis queues work now (ZSET) | [02_redis_queue.md](02_redis_queue.md), [15_advanced_queue.md](15_advanced_queue.md) |
| Worker retries / shutdown | [03_worker.md](03_worker.md) |
| Why Postgres vs Redis | [04_postgresql.md](04_postgresql.md) |
| Handlers + lifecycle | [05_job_handlers.md](05_job_handlers.md) |
| React UI / live updates | [06_react_vite.md](06_react_vite.md), [09_polling_websockets.md](09_polling_websockets.md) |
| Tests & CI | [10_testing.md](10_testing.md), [11_ci.md](11_ci.md) |
| Docker / migrations | [12_docker_app.md](12_docker_app.md), [13_migrations.md](13_migrations.md) |
| Logs & metrics | [14_observability.md](14_observability.md) |
| API key / rate limit / SSRF | [16_auth_security.md](16_auth_security.md) |

## Key files

- `app/main.py` — routes
- `app/queue.py` — Redis ready / delayed / DLQ / events
- `app/worker.py` — claim → run → succeed / retry / dead
- `app/jobs/handlers.py` — `sleep` / `http_fetch` / `fail`
- `web/src/App.tsx` — WebSocket + polling UI
