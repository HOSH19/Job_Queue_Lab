# Observability

If you cannot see the queue, you cannot operate it.

## Structured logs

Set `LOG_JSON=true` to emit JSON logs (`app/logging_config.py`). Workers include `job_id` in log `extra` so you can grep one job across API + worker.

Every HTTP response gets an `X-Request-Id` header (`app/main.py` middleware) for correlating client reports with server logs.

## Prometheus metrics

`GET /metrics` exposes:

- `jobqueue_jobs_enqueued_total`
- `jobqueue_jobs_succeeded_total` / `failed` / `retried` / `dead`
- `jobqueue_job_duration_seconds`
- `jobqueue_queue_depth`

Scrape with Prometheus or open the endpoint while demos run.

## UI timeline

Job detail shows attempt counts, last error, and dead-letter outcome so operators do not need SQL to debug a failure.
