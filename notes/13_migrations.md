# Schema migrations (Alembic)

`Base.metadata.create_all()` is fine for a brand-new lab database. Production-shaped workflows use **migrations** so schema changes are versioned and reversible.

## Pieces

- [`alembic.ini`](../alembic.ini) + [`alembic/env.py`](../alembic/env.py) — wired to `app.models.Base` and `DATABASE_URL`.
- [`alembic/versions/001_initial_jobs.py`](../alembic/versions/001_initial_jobs.py) — creates `jobs` including `priority`, `run_at`, `idempotency_key`.

```bash
make migrate
# or
alembic upgrade head
```

## Habit

1. Change the SQLAlchemy model.
2. Generate a revision (`alembic revision --autogenerate -m "..."`).
3. Review the script.
4. Apply with `upgrade head`.

Never hand-edit production tables without a revision — the next deploy will disagree with reality.
