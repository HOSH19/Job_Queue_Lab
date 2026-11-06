# Job handlers and lifecycle

Handlers are the **units of work**. The worker looks up `job.type` and calls the matching function with the JSON `payload`.

Code: [`app/jobs/handlers.py`](../app/jobs/handlers.py)

## Built-in types

| Type | Payload | Behavior |
|------|---------|----------|
| `sleep` | `{ "seconds": 0–10 }` | Blocks for N seconds; returns `{ "slept": N }` |
| `http_fetch` | `{ "url": "..." }` | GET the URL; stores status code + body length |
| `fail` | `{ "message": "..." }` | Always raises — for retry demos |

`sleep` proves async timing in the UI. `http_fetch` is a realistic I/O-bound job. `fail` teaches retries without flaky code.

## Lifecycle

```text
queued → running → succeeded
                 → dead            (attempts exhausted → also pushed to DLQ)
queued → cancelled                 (API cancel before worker claims; Redis id removed)
running → queued                   (retry after error)
```

Cancel is only allowed while `queued`. Once the worker has set `running`, cancel returns `409`. Permanent failure is status **`dead`** (not `failed`) so you can tell “gave up + DLQ” from older docs that said `failed`.

## Adding a new job type

1. Write a function `(payload: dict) -> dict` in `handlers.py`.
2. Register it in `HANDLERS`.
3. Add the enum value in [`app/models.py`](../app/models.py) / [`app/schemas.py`](../app/schemas.py).
4. Teach the React form a field or two (optional).

Keep handlers **pure-ish**: take payload, return a JSON-serializable result or raise. Side effects (HTTP, sleep) are fine; don’t touch Redis/DB inside the handler — the worker owns status transitions.

## Experiment

1. Run `sleep` with 2 seconds — table should show `running` briefly.
2. Run `fail` with `max_attempts` 1 — watch it land in `dead` and appear on `GET /dlq`.
3. Enqueue a long `sleep`, cancel immediately if still `queued`.
4. Run `http_fetch` against `https://httpbin.org/get` and read the detail panel.
5. Try `http_fetch` with `http://localhost/` — should be rejected (SSRF guard).
