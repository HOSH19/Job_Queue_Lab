# POST and GET (and a bit of HTTP)

The lab UI and API talk over **HTTP**. Methods tell the server *what kind of action* you want.

## The ones we use

| Method | Meaning (convention) | In this lab |
|--------|----------------------|-------------|
| **GET** | Read data — should not change server state | `GET /jobs`, `GET /jobs/{id}`, `GET /health` |
| **POST** | Create or trigger an action | `POST /jobs`, `POST /jobs/{id}/cancel` |

Code: [`app/main.py`](../app/main.py) · client: [`web/src/api/client.ts`](../web/src/api/client.ts)

## GET

- Safe to refresh / bookmark / poll repeatedly.
- Parameters often go in the **URL** (`?status=queued`) or path (`/jobs/{id}`).
- Our list endpoint: `GET /jobs` → JSON array of jobs.
- Our detail endpoint: `GET /jobs/{id}` → one job.

Polling the UI is just **GET in a loop** while work is in flight.

## POST

- Used when something should **happen**: create a job, cancel a job.
- Body is usually **JSON** (`Content-Type: application/json`).
- Creating a job:

```http
POST /jobs
Content-Type: application/json

{"type":"sleep","payload":{"seconds":2}}
```

- Response is often `201 Created` with the new resource (we return the job row).

## Why not PUT/PATCH/DELETE here?

Those are common for full CRUD APIs. This lab keeps the surface small:

- Create → `POST`
- Read → `GET`
- Cancel → `POST .../cancel` (an action), not `DELETE`

You *could* model cancel as `DELETE /jobs/{id}`; we chose an explicit action URL so “cancel while queued” is obvious.

## Status codes you’ll see

| Code | Meaning |
|------|---------|
| `200` | OK (GET, cancel) |
| `201` | Created (new job) |
| `404` | Job id not found |
| `409` | Conflict (e.g. cancel when already `running`) |
| `503` | Redis enqueue failed |

## Experiment

1. Open http://localhost:8000/docs and try `POST /jobs` then `GET /jobs/{id}`.
2. In the browser DevTools → Network, submit a job from the UI — find the `POST` and the following `GET` polls.
3. Call cancel on a `succeeded` job — expect `409`.
