# FastAPI (the HTTP API)

FastAPI is the **front door** of the lab. Browsers and tools talk to it over HTTP; it never runs the slow job work itself.

## What it does here

| Route | Role |
|-------|------|
| `POST /jobs` | Create a job row, push its id onto Redis, return immediately |
| `GET /jobs` | List recent jobs (optional status filter) |
| `GET /jobs/{id}` | One job’s status, result, or error |
| `POST /jobs/{id}/cancel` | Mark `cancelled` if still `queued` |
| `GET /health` | Liveness + Redis ping |
| `/docs` | Interactive Swagger UI (built-in) |

Code: [`app/main.py`](../app/main.py) · schemas: [`app/schemas.py`](../app/schemas.py)

## Why FastAPI for this lab

- **Pydantic models** validate request bodies (`type`, `payload`) and shape responses.
- **Dependency injection** (`Depends(get_db)`) gives each request a database session.
- **OpenAPI** at `/docs` lets you try the API without the React UI.
- **CORS middleware** allows the Vite app on `:5173` to call `:8000` in the browser.

## Request path on create

1. Validate `JobCreate` (type + payload).
2. Insert a PostgreSQL row with status `queued`.
3. `LPUSH` the job id to Redis.
4. Return `JobOut` — usually still `queued` when the response lands.

The API’s job is to be **fast and reliable at accepting work**, not to sleep, fetch URLs, or retry failures. That belongs to the [worker](03_worker.md).

## Config

Settings live in [`app/config.py`](../app/config.py) (from `.env`): Redis URL, PostgreSQL path, queue key, default `max_attempts`, CORS origins.

## Experiment

1. Open http://localhost:8000/docs and create a `sleep` job.
2. Hit `GET /jobs/{id}` a few times while the worker runs — watch status change without using the UI.
3. Stop Redis and create a job — enqueue fails and the API returns `503`.
