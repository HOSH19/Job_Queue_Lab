# PostgreSQL (durable job state)

PostgreSQL holds the **source of truth** for every job: what was requested, where it is in the lifecycle, and what came back.

This lab talks to Postgres through **SQLAlchemy** + the **psycopg** driver. The ORM models stay the same whether you use SQLite or Postgres — only `DATABASE_URL` changes.

Code: [`app/models.py`](../app/models.py) · [`app/db.py`](../app/db.py)  
Compose service: [`docker-compose.yml`](../docker-compose.yml)  
Default URL: `postgresql+psycopg://jobqueue:jobqueue@localhost:5432/jobqueue`

## Why Postgres (not only Redis)?

Redis is great for a fast queue of ids, but:

- Results and errors need to survive process restarts.
- The UI polls **status history**, not “who is next in line.”
- Cancel / succeeded / failed are business states, not queue positions.

So: **Redis = wake the worker; PostgreSQL = remember the job.**

## Why Postgres instead of SQLite?

| | SQLite | PostgreSQL |
|--|--------|------------|
| Setup | One file | Separate server (Docker here) |
| Concurrent writers | Limited | Built for many clients |
| Typical use | Local prototypes | Shared apps, workers, APIs |
| Learning value | Simplicity | Real client/server SQL |

The API and worker are **two processes** writing the same table. Postgres is a better fit for that pattern than a single-file DB.

## Connection string shape

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
                 ^
                 SQLAlchemy dialect + driver
```

- `postgresql` — database family
- `psycopg` — Python driver (v3). Older docs often show `psycopg2`.

Set it in `.env` as `DATABASE_URL`. On startup, `init_db()` runs `CREATE TABLE` if needed.

## Job row (simplified)

| Column | Purpose |
|--------|---------|
| `id` | UUID primary key (also the Redis message) |
| `type` | Which handler to run |
| `payload` | JSON arguments (stored as text) |
| `status` | `queued` / `running` / `succeeded` / `failed` / `cancelled` |
| `result` / `error` | Outcome |
| `attempts` / `max_attempts` | Retry bookkeeping |
| `created_at` / `updated_at` | Timestamps for the UI |

## Who writes what

| Actor | Writes |
|-------|--------|
| **API** | Insert `queued`; set `cancelled` |
| **Worker** | `running` → `succeeded` / `failed` / back to `queued` on retry |

Both must use the **same** `DATABASE_URL`.

## Useful local commands

```bash
docker compose up -d postgres

# psql inside the container
docker compose exec postgres psql -U jobqueue -d jobqueue

# then in psql:
\dt
SELECT id, type, status, attempts FROM jobs ORDER BY created_at DESC LIMIT 10;
```

`/health` reports `database: up` when `SELECT 1` succeeds.

## Experiment

1. Start compose, API, and worker. Submit a job — confirm it appears in `psql`.
2. Stop Postgres (`docker compose stop postgres`) and hit `/health` — expect `database: down` / degraded.
3. Start Postgres again — tables persist in the `postgres_data` volume; old jobs are still there.
4. (Optional) Point `DATABASE_URL` at `sqlite:///./data/jobs.db` to see the same models on SQLite — then switch back.
