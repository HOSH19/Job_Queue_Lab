# Advanced queue semantics

Beyond a plain FIFO list:

## Priority + ready set

Ready jobs live in a Redis **ZSET** (`QUEUE_KEY`). Score encodes `-priority` then timestamp so `BZPOPMIN` pops the highest priority first (`app/queue.py`).

## Delayed / scheduled jobs

Future `run_at` values go to `DELAYED_KEY`. The worker periodically **promotes** due members into the ready ZSET.

## Dead-letter queue (DLQ)

After `max_attempts`, the job status becomes `dead` and the id is `LPUSH`ed to `DLQ_KEY`. Inspect via `GET /dlq`.

## Idempotency

Send `Idempotency-Key` on `POST /jobs`. A second request with the same key returns the original job instead of enqueueing twice.

## Safer cancel

Cancel sets DB status to `cancelled` **and** removes the id from ready/delayed ZSETs so the worker does not needlessly claim it.

## Multi-worker

```bash
docker compose up --scale worker=2
```

Two processes compete on `BZPOPMIN` — at-least-once delivery still applies; handlers should tolerate rare double delivery after crashes.
