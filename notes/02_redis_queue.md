# Redis (the work queue)

In this lab Redis is **not a cache**. It is a **queue of job ids** waiting for a worker.

## Why a queue at all

HTTP requests should return quickly. Slow work (sleep, HTTP fetch, anything that can fail) runs in another process. Redis is the hand-off:

```text
API  --ZADD job_id-->  Redis ZSET  --BZPOPMIN-->  Worker
         \-- delayed ZSET (future run_at) --promote-->/
```

Early versions of this lab used a plain list (`LPUSH` / `BRPOP`). The queue now uses sorted sets so **priority** and **delayed** jobs work — see [15_advanced_queue.md](15_advanced_queue.md).

Code: [`app/queue.py`](../app/queue.py) · started via [`docker-compose.yml`](../docker-compose.yml)

## Commands we use

| Call | Meaning |
|------|---------|
| `ZADD queue_key score job_id` | Enqueue ready work (score encodes priority) |
| `BZPOPMIN queue_key timeout` | Worker blocks until the highest-priority id appears |
| `ZADD delayed_key timestamp job_id` | Schedule for later |
| `LPUSH dlq_key job_id` | Dead-letter after retries exhausted |
| `PUBLISH events_channel payload` | Fan-out UI WebSocket events |
| `PING` | Health check from `/health` |

Default keys: `jobqueue:jobs`, `jobqueue:delayed`, `jobqueue:dlq` (see `.env`).

## Redis vs PostgreSQL (not the same thing)

They are **different systems** with different jobs in this lab:

| | **Redis** | **PostgreSQL** |
|--|-----------|----------------|
| **Role here** | Work **queue** | Durable **job database** |
| **Stores** | Job **ids** waiting to run | Full job rows (type, payload, status, result, error, attempts) |
| **Lifetime** | Temporary hand-off to the worker | Long-lived history the UI polls |
| **Port** | `6379` | `5432` |
| **If it restarts** | Queued ids can be lost | Job rows persist (Docker volume) |

```text
API creates job in PostgreSQL (status: queued)
     → pushes id into Redis
Worker pops id from Redis
     → loads/updates that job in PostgreSQL
```

**Redis = “wake up, do this next.”**  
**Postgres = “here’s what the job is and how it turned out.”**

See also [04_postgresql.md](04_postgresql.md). Production systems often add “reclaim stuck `queued`/`running` jobs” after a Redis restart; this lab keeps that out of scope.

## Why `BRPOP` instead of polling Redis

`BRPOP` **blocks** the worker until work arrives (or a short timeout). That avoids a tight loop hammering Redis when the queue is empty. After timeout, the worker loops and can notice a shutdown signal.

## Failure modes

- **Redis down** — API cannot enqueue (`503`); `/health` shows `redis: down`.
- **Worker down** — jobs stay `queued` in PostgreSQL forever until a worker starts.
- **Multiple workers** — each `BRPOP` takes one id; several workers share the list (simple horizontal scale).

## Experiment

1. Start API only (no worker). Submit a job → stays `queued`.
2. Start the worker → job moves to `running` then `succeeded`.
3. Run two workers and enqueue several `sleep` jobs — work is shared across processes.
