# CORS (Cross-Origin Resource Sharing)

Browsers enforce a security rule: a page from one **origin** cannot freely call APIs on another origin unless the API allows it.

## What is an origin?

```text
http://localhost:5173
│      │         │
│      │         └─ port
│      └─ host
└─ scheme
```

In this lab:

| App | Origin |
|-----|--------|
| React (Vite) | `http://localhost:5173` |
| FastAPI | `http://localhost:8000` |

Different ports ⇒ **different origins**, even on the same machine.

## What goes wrong without CORS

If the browser JS on `:5173` does `fetch('http://localhost:8000/jobs')`, the browser first checks CORS. If the API doesn’t send the right headers, the browser **blocks** the response (you’ll see a CORS error in DevTools — the server may have answered fine).

## What we do in this lab

FastAPI adds CORS middleware:

```python
allow_origins=["http://localhost:5173"]  # from CORS_ORIGINS in .env
```

Code: [`app/main.py`](../app/main.py) · config: [`app/config.py`](../app/config.py)

That tells the browser: “yes, the Vite app may read responses from this API.”

## Vite proxy (the other half)

In **dev**, Vite also **proxies** `/jobs` and `/health` to `:8000`:

```ts
// web/vite.config.ts
proxy: {
  '/jobs': 'http://127.0.0.1:8000',
  '/health': 'http://127.0.0.1:8000',
}
```

So the page can call `fetch('/jobs')` — same origin as the page (`:5173`), and Vite forwards to the API. That avoids CORS for those relative URLs **during local dev**.

CORS still matters if:

- You point the client at `http://localhost:8000` directly, or
- You host the SPA and API on different domains in production.

## Simple mental model

| Path | Who cares about CORS? |
|------|------------------------|
| Browser → API on another origin | Yes — API must allow the SPA origin |
| Browser → Vite → API (proxy) | Browser sees same origin; proxy is server-side |
| `curl` / worker / Python | No — CORS is a **browser** rule |

## Experiment

1. With the UI open, DevTools → Network: relative `/jobs` requests go to `:5173` (proxied).
2. Temporarily call `fetch('http://localhost:8000/health')` from the console — works because CORS is enabled for `:5173`.
3. Remove `:5173` from `CORS_ORIGINS`, restart the API, retry a direct `:8000` fetch — browser should block it.
