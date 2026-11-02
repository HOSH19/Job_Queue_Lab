# Redis (the work queue)

In this lab Redis is **not a cache**. It is a **queue of job ids** waiting for a worker.

## Why a queue at all

HTTP requests should return quickly. Slow work (sleep, HTTP fetch, anything that can fail) runs in another process. Redis is the hand-off:

```text
API  --LPUSH job_id-->  Redis list  --BRPOP-->  Worker
```

Code: [`app/queue.py`](../app/queue.py) · started via [`docker-compose.yml`](../docker-compose.yml)

## Commands we use

| Call | Meaning |
|------|---------|
| `LPUSH queue_key job_id` | Enqueue (push to the left) |
| `BRPOP queue_key timeout` | Worker blocks until an id appears (or timeout) |
| `PING` | Health check from `/health` |

Default key: `jobqueue:jobs` (`QUEUE_KEY` in `.env`).

## What Redis stores vs SQLite

| Store | Contents |
|-------|----------|
| **Redis** | Only **ids** of jobs ready to run (ephemeral work signals) |
| **SQLite** | Full job record: type, payload, status, result, error, attempts |

If Redis restarts, queued ids can be lost — the durable truth is SQLite. Production systems often add “reclaim stuck `queued`/`running` jobs” recovery; this lab keeps that out of scope.

## Why `BRPOP` instead of polling Redis

`BRPOP` **blocks** the worker until work arrives (or a short timeout). That avoids a tight loop hammering Redis when the queue is empty. After timeout, the worker loops and can notice a shutdown signal.

## Failure modes

- **Redis down** — API cannot enqueue (`503`); `/health` shows `redis: down`.
- **Worker down** — jobs stay `queued` in SQLite forever until a worker starts.
- **Multiple workers** — each `BRPOP` takes one id; several workers share the list (simple horizontal scale).

## Experiment

1. Start API only (no worker). Submit a job → stays `queued`.
2. Start the worker → job moves to `running` then `succeeded`.
3. Run two workers and enqueue several `sleep` jobs — work is shared across processes.
