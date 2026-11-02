# SQLite (durable job state)

SQLite holds the **source of truth** for every job: what was requested, where it is in the lifecycle, and what came back.

Code: [`app/models.py`](../app/models.py) · [`app/db.py`](../app/db.py)  
Default file: `data/jobs.db` (`DATABASE_URL` in `.env`)

## Why not only Redis?

Redis is great for a fast queue of ids, but:

- Results and errors need to survive process restarts.
- The UI polls **status history**, not “who is next in line.”
- Cancel / succeeded / failed are business states, not queue positions.

So: **Redis = wake the worker; SQLite = remember the job.**

## Job row (simplified)

| Column | Purpose |
|--------|---------|
| `id` | UUID primary key (also the Redis message) |
| `type` | Which handler to run (`sleep`, `http_fetch`, `fail`) |
| `payload` | JSON arguments for the handler |
| `status` | `queued` / `running` / `succeeded` / `failed` / `cancelled` |
| `result` | JSON on success |
| `error` | Last error string on failure / retry |
| `attempts` / `max_attempts` | Retry bookkeeping |
| `created_at` / `updated_at` | Timestamps for the UI |

## Who writes what

| Actor | Writes |
|-------|--------|
| **API** | Insert `queued`; set `cancelled` |
| **Worker** | `running` → `succeeded` / `failed` / back to `queued` on retry |

Both use SQLAlchemy sessions. The API and worker must point at the **same** database file.

## Lab tradeoffs

- SQLite is simple (one file, no extra server). Fine for a local lab.
- Concurrent writers are limited; a production queue often uses Postgres.
- Schema is created on startup (`init_db`) — no migration tool in this lab.

## Experiment

1. After a few jobs, open `data/jobs.db` with any SQLite browser and inspect the `jobs` table.
2. Stop the API, leave the worker running — the worker still updates rows.
3. Restart the API — list endpoint still shows history (Redis does not).
