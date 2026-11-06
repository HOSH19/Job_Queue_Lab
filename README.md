# Job Queue Lab

HTTP enqueue → Redis queue → worker → Postgres status, plus a small React UI.

```text
UI ──POST /jobs──► FastAPI ──insert──► Postgres
                      │
                      └──ZADD──► Redis ──BZPOPMIN──► Worker ──update──► Postgres
                                                              │
                                                         pub/sub ──► /ws/jobs ──► UI
```

Lifecycle: `queued` → `running` → `succeeded` | `dead` (after retries). Cancel only while `queued`.

## Run

```bash
make install && make up && make migrate
make api      # :8000
make worker
make web      # :5173
```

Or all-in-Docker: `docker compose up --build`  
Docs: http://localhost:8000/docs · Metrics: `/metrics` · Tests: `make test`

## Job types

| Type | What it does |
|------|----------------|
| `sleep` | Sleep N seconds (UI timing demo) |
| `http_fetch` | GET a URL (SSRF-checked) |
| `fail` | Always errors (retry / DLQ demo) |

## Learn more

Read [`notes/`](notes/) in order — especially [`00_overview.md`](notes/00_overview.md) for the big picture, then `10`–`16` for the SE practices added on top of the core lab.
