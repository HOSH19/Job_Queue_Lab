"""Convert ORM rows into API response models."""

from __future__ import annotations

import json

from app.models import Job, JobStatus
from app.schemas import JobOut


def job_to_out(job: Job) -> JobOut:
    """Map a Job ORM instance to JobOut."""
    return JobOut(
        id=job.id,
        type=job.type,
        payload=json.loads(job.payload or "{}"),
        status=JobStatus(job.status),
        result=json.loads(job.result) if job.result else None,
        error=job.error,
        attempts=job.attempts,
        max_attempts=job.max_attempts,
        priority=job.priority,
        run_at=job.run_at,
        idempotency_key=job.idempotency_key,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
