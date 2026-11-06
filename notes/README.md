# Notes

Start here: **[00_overview.md](00_overview.md)**.

| # | File | Topic |
|---|------|--------|
| 00 | [00_overview.md](00_overview.md) | Big picture + reading map |
| 01 | [01_fastapi.md](01_fastapi.md) | HTTP API, Pydantic, CORS |
| 02 | [02_redis_queue.md](02_redis_queue.md) | Redis queue (ZSET / delayed / DLQ) |
| 03 | [03_worker.md](03_worker.md) | Worker process, retries, shutdown |
| 04 | [04_postgresql.md](04_postgresql.md) | Durable job rows vs Redis |
| 05 | [05_job_handlers.md](05_job_handlers.md) | Job types & lifecycle |
| 06 | [06_react_vite.md](06_react_vite.md) | React UI, Vite proxy |
| 07 | [07_http_methods.md](07_http_methods.md) | GET vs POST |
| 08 | [08_cors.md](08_cors.md) | CORS vs proxy |
| 09 | [09_polling_websockets.md](09_polling_websockets.md) | Polling vs WebSockets |
| 10 | [10_testing.md](10_testing.md) | pytest + Vitest |
| 11 | [11_ci.md](11_ci.md) | GitHub Actions, ruff, pre-commit |
| 12 | [12_docker_app.md](12_docker_app.md) | Dockerize API + worker |
| 13 | [13_migrations.md](13_migrations.md) | Alembic |
| 14 | [14_observability.md](14_observability.md) | Logs, metrics, request ids |
| 15 | [15_advanced_queue.md](15_advanced_queue.md) | Priority, delay, DLQ, idempotency |
| 16 | [16_auth_security.md](16_auth_security.md) | API key, rate limit, SSRF |

**Core idea:** API accepts work quickly; a worker does the slow part later; Postgres remembers what happened.
