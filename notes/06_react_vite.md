# React + Vite (the frontend)

The UI is a small **React + TypeScript** app so you see a real split stack: browser on `:5173`, API on `:8000`.

Code: [`web/`](../web/) · API client: [`web/src/api/client.ts`](../web/src/api/client.ts)

## What “frontend” means here

Not just HTML/CSS. The browser runs JavaScript that:

1. Submits jobs (`POST /jobs`).
2. Lists and selects jobs (`GET /jobs`).
3. **Polls** every ~1s while any job is `queued` or `running`.
4. Cancels queued jobs (`POST /jobs/{id}/cancel`).
5. Shows health (API + Redis) in the header.

Components: `JobForm`, `JobTable`, `JobDetail` under [`web/src/components/`](../web/src/components/).

## Vite’s role

Vite is the **dev server and bundler**:

- Serves the React app with hot reload.
- **Proxies** `/jobs` and `/health` to `http://127.0.0.1:8000` so `fetch('/jobs')` works without hard-coding the API host.

Config: [`web/vite.config.ts`](../web/vite.config.ts)

## CORS

Even with a proxy, the API still enables CORS for `http://localhost:5173` ([`app/main.py`](../app/main.py)). That matters if you call the API origin directly or change how the client is hosted.

## Polling (not websockets)

This lab uses simple polling:

- Cheap to understand.
- Matches “ask the API for current SQLite state.”
- Good enough for a local dashboard.

Production UIs often use websockets or SSE for push updates — out of scope here.

## Run

```bash
cd web
npm install
npm run dev
```

Open http://localhost:5173 (API + worker must already be running).

## Experiment

1. Submit a 5s `sleep` and watch the badge flip without refreshing the page.
2. Open DevTools → Network: see repeated `GET /jobs` while jobs are active; polling stops when all are terminal.
3. Stop the API — the banner should show a load error.
