# Auth & hardening

## API key

Set `API_KEY` in `.env`. Mutating routes (`POST /jobs`, cancel) then require header:

```http
X-API-Key: your-secret
```

Leave `API_KEY` empty for local demos without auth (`app/auth.py`).

The UI reads an optional key from `localStorage.jobqueue_api_key`.

## Rate limiting

`slowapi` limits enqueue by client IP using `RATE_LIMIT` (default `60/minute`).

## SSRF protection on `http_fetch`

The handler resolves the URL host and rejects localhost / private / link-local / reserved addresses (`app/jobs/handlers.py`). Redirects are disabled so a public URL cannot bounce into the internal network.

Still not a full SSRF suite (DNS rebinding, etc.) — enough to teach the threat model.
