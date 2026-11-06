"""Business logic for creating, listing, and cancelling jobs."""

from __future__ import annotations

import json
import logging
import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.metrics import JOBS_ENQUEUED
from app.models import Job, JobStatus, utcnow
from app.queue import enqueue, publish_event, remove_from_queue
from app.schemas import JobCreate, JobOut
from app.serializers import job_to_out

log = logging.getLogger("api")
settings = get_settings()


def find_by_idempotency(db: Session, key: str) -> Job | None:
    """Return an existing job for an idempotency key, if any."""
    return db.query(Job).filter(Job.idempotency_key == key).one_or_none()


def create_job_row(
    db: Session,
    body: JobCreate,
    idempotency_key: str | None,
) -> JobOut:
    """Persist a queued job, enqueue it, and return the API shape."""
    if idempotency_key:
        existing = find_by_idempotency(db, idempotency_key)
        if existing is not None:
            return job_to_out(existing)

    job = _build_job(body, idempotency_key)
    db.add(job)
    twin = _commit_or_twin(db, job, idempotency_key)
    if twin is not None:
        return job_to_out(twin)

    _enqueue_or_fail(db, job)
    JOBS_ENQUEUED.labels(type=job.type).inc()
    publish_event({"event": "enqueued", "job_id": job.id, "type": job.type, "status": job.status})
    log.info("enqueued job %s type=%s", job.id, job.type, extra={"job_id": job.id})
    return job_to_out(job)


def _build_job(body: JobCreate, idempotency_key: str | None) -> Job:
    """Construct a queued Job ORM row from the request body."""
    max_attempts = body.max_attempts if body.max_attempts is not None else settings.max_attempts
    return Job(
        id=str(uuid.uuid4()),
        type=body.type.value,
        payload=json.dumps(body.payload),
        status=JobStatus.queued.value,
        attempts=0,
        max_attempts=max_attempts,
        priority=body.priority,
        run_at=body.run_at,
        idempotency_key=idempotency_key,
    )


def _commit_or_twin(
    db: Session,
    job: Job,
    idempotency_key: str | None,
) -> Job | None:
    """Commit the insert. On unique race, return the winning twin job."""
    try:
        db.commit()
        db.refresh(job)
        return None
    except IntegrityError as exc:
        db.rollback()
        if idempotency_key:
            existing = find_by_idempotency(db, idempotency_key)
            if existing is not None:
                return existing
        raise HTTPException(status_code=409, detail="could not create job") from exc


def _enqueue_or_fail(db: Session, job: Job) -> None:
    """Push to Redis or mark the row failed and raise 503."""
    try:
        enqueue(job.id, priority=job.priority, run_at=job.run_at)
    except Exception as exc:
        job.status = JobStatus.failed.value
        job.error = f"failed to enqueue: {exc}"
        job.updated_at = utcnow()
        db.commit()
        db.refresh(job)
        raise HTTPException(status_code=503, detail=f"Redis enqueue failed: {exc}") from exc


def list_job_rows(
    db: Session,
    status: JobStatus | None,
    limit: int,
) -> list[JobOut]:
    """Return newest jobs, optionally filtered by status."""
    query = db.query(Job).order_by(Job.created_at.desc())
    if status is not None:
        query = query.filter(Job.status == status.value)
    return [job_to_out(j) for j in query.limit(limit).all()]


def get_job_row(db: Session, job_id: str) -> JobOut:
    """Fetch one job or raise 404."""
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job_to_out(job)


def cancel_job_row(db: Session, job_id: str) -> JobOut:
    """Cancel a queued job and drop it from Redis when possible."""
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != JobStatus.queued.value:
        raise HTTPException(status_code=409, detail=f"cannot cancel job in status {job.status}")
    job.status = JobStatus.cancelled.value
    job.updated_at = utcnow()
    db.commit()
    db.refresh(job)
    try:
        remove_from_queue(job_id)
    except Exception:
        log.exception("failed to remove %s from redis queue", job_id)
    publish_event({"event": "cancelled", "job_id": job.id, "status": job.status})
    return job_to_out(job)
