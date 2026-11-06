# Polling vs WebSockets

Jobs finish **asynchronously**. The UI needs a way to learn when status changes from `queued` → `running` → `succeeded` / `failed`.

## What this lab uses: polling

**Polling** = ask the server on a timer: “any updates?”

In the React app:

1. After load, `GET /jobs`.
2. While any job is `queued` or `running`, `setInterval` every ~1s calls `GET /jobs` again.
3. When all jobs are terminal, polling **stops** (no busy loop forever).

Code: [`web/src/App.tsx`](../web/src/App.tsx)

```text
UI  --GET /jobs-->  API  --read-->  PostgreSQL
     (every ~1s while active)
```

### Pros
- Simple to build and debug (just HTTP GET).
- Works with our existing REST API — no extra protocol.
- Easy to reason about with DevTools Network tab.

### Cons
- Extra requests when nothing changed.
- Updates arrive with up to ~1s delay (the interval).
- At huge scale, many clients polling can load the API.

For a local lab dashboard, polling is enough.

## What you might use later: WebSockets (or SSE)

**WebSockets** keep a long-lived two-way connection. The server can **push** “job 123 succeeded” the moment it happens.

```text
UI  <==persistent socket==>  API
         (server pushes events)
```

**SSE (Server-Sent Events)** is one-way push (server → browser) over HTTP — also common for status streams.

### Pros
- Lower latency updates.
- Fewer “empty” requests when idle.

### Cons
- More moving parts (connection lifecycle, reconnects, load balancers).
- API must broadcast events when the worker updates Postgres (or the UI still polls DB somehow).

**This lab now implements WebSockets** at `/ws/jobs`: the worker publishes Redis pub/sub events and the API forwards them to browsers. The UI still falls back to polling if the socket drops.

## How it fits the stack

| Piece | Role |
|-------|------|
| Worker | Writes new status to **PostgreSQL** and publishes Redis events |
| API | Serves REST + `/ws/jobs` push |
| UI | Prefers WebSocket refresh; polls if the socket is down |

Redis is used both to wake workers and to fan out UI events.

## Experiment

1. Submit a 5s `sleep`. In DevTools → Network, watch `GET /jobs` repeat while status is active, then stop.
2. Change the interval in `App.tsx` from `1000` to `3000` — updates feel slower.
3. Mentally map a WebSocket design: worker finishes → API publishes event → UI updates one row without listing all jobs.
