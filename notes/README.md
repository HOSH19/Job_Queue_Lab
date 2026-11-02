# Notes — stack pieces in this lab

Concept explainers for each part of Job Queue Lab. Read in order if you're new; jump by layer when debugging.

| File | Topic |
|------|--------|
| [01_fastapi.md](01_fastapi.md) | HTTP API, Pydantic models, CORS |
| [02_redis_queue.md](02_redis_queue.md) | Redis as a work queue (`LPUSH` / `BRPOP`) |
| [03_worker.md](03_worker.md) | Separate worker process, retries, shutdown |
| [04_postgresql.md](04_postgresql.md) | PostgreSQL durable job rows vs Redis queue messages |
| [05_job_handlers.md](05_job_handlers.md) | Job types, lifecycle, cancel |
| [06_react_vite.md](06_react_vite.md) | React UI, polling, Vite proxy |

Core idea: **API accepts work quickly; a worker does the slow part later; PostgreSQL remembers what happened.**
