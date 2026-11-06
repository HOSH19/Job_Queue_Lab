# Testing

Automated tests catch regressions before you click around the UI.

## Backend (`pytest`)

- **API tests** use FastAPI's `TestClient` with an in-memory SQLite DB and mocked Redis (`tests/test_api.py`).
- **Handler tests** exercise pure business logic without Redis/Postgres (`tests/test_handlers.py`).
- **Queue tests** use `fakeredis` so priority / delayed / DLQ behavior is real Redis semantics without Docker (`tests/test_queue.py`).
- **Worker tests** call `process_job` with a real SQLite session and mocked side effects (`tests/test_worker.py`).

Run:

```bash
pytest -q
```

## Frontend (`vitest` + Testing Library)

Component tests render React in jsdom and assert user-visible behavior (`web/src/components/__tests__/`).

```bash
cd web && npm test -- --run
```

## Why both layers?

| Layer | What it proves |
|-------|----------------|
| Handlers / queue | Core rules without HTTP |
| API | Status codes, validation, auth headers |
| Worker | Lifecycle transitions and retries |
| UI | Forms and badges still make sense after refactors |
