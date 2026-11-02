# Worker (the background process)

The worker is a **separate Python process** from the API. It pulls job ids from Redis, loads the job from PostgreSQL, runs a handler, and writes the outcome back.

Run it with:

```bash
python -m app.worker
```

Code: [`app/worker.py`](../app/worker.py)

## Main loop

1. `BRPOP` the queue (short timeout).
2. Load the job from PostgreSQL by id.
3. Skip if missing, already finished, or `cancelled`.
4. Set status `running`, increment `attempts`.
5. Call the handler for `job.type`.
6. On success → `succeeded` + JSON `result`.
7. On failure → re-queue if attempts remain, else `failed` + `error`.

## Why a separate process

| Same process as API | Separate worker |
|---------------------|-----------------|
| One crash takes down HTTP | API can stay up if a job crashes |
| Blocking work stalls other requests | Slow jobs don’t block `/jobs` |
| Hard to scale workers alone | Run N worker processes independently |

This split is the core backend lesson of the lab.

## Retries

On handler exception:

- If `attempts < max_attempts` → status back to `queued`, brief backoff, `LPUSH` again.
- Else → `failed` with the error string.

Try a `fail` job with `max_attempts: 2` and watch attempts climb in the UI.

## Graceful shutdown

`SIGINT` / `SIGTERM` set a flag so the worker finishes the **current** job, then exits — instead of dying mid-handler with a stuck `running` row.

## Experiment

1. Start the worker and watch its logs while submitting jobs from the UI.
2. Submit `fail` — logs show the exception and re-queue messages.
3. Ctrl+C the worker while a long `sleep` is running — it finishes that job before exit (if the signal is handled mid-loop after the job).
