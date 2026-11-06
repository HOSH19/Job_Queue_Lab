# Dockerizing API + worker

Infra containers (Redis, Postgres) were always in Compose. The app itself can also run in containers so teammates share one command.

## Layout

- [`Dockerfile`](../Dockerfile) — Python image with API code; same image runs the worker via a different `command`.
- [`docker-compose.yml`](../docker-compose.yml) — `api` + `worker` services talk to `redis` / `postgres` on the Compose network.

```bash
# infra only (local uvicorn/worker)
make up

# full stack in Docker
make stack
# competing consumers:
docker compose up --build --scale worker=2
```

## Why two processes?

The API should stay responsive. Slow work belongs in workers. Scaling workers (`--scale worker=2`) shows **competing consumers** on one Redis ZSET — each job is popped once.

## Makefile DX

[`Makefile`](../Makefile) wraps common tasks: `up`, `api`, `worker`, `web`, `test`, `lint`, `migrate`.
