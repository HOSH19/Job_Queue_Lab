"""Claim a single job id and run its handler with retry / DLQ."""

from __future__ import annotations

import json
import logging
import time

from app.db import SessionLocal
from app.jobs.handlers import run_handler
from app.metrics import JOB_DURATION, JOBS_DEAD, JOBS_FAILED, JOBS_RETRIED, JOBS_SUCCEEDED
from app.models import Job, JobStatus, utcnow
from app.queue import enqueue, publish_event, push_dlq

log = logging.getLogger("worker")


def process_job(job_id: str) -> None:
    """Load, run, and finalize one job from the queue."""
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not _claimable(job, job_id):
            return
        _mark_running(db, job)
        _run_and_finalize(db, job)
    finally:
        db.close()


def _claimable(job: Job | None, job_id: str) -> bool:
    """Return True if this worker should execute the job."""
    if job is None:
        log.warning("job %s not found in DB, skipping", job_id)
        return False
    if job.status == JobStatus.cancelled.value:
        log.info("job %s cancelled, skipping", job_id)
        return False
    if job.status not in (JobStatus.queued.value, JobStatus.running.value):
        log.info("job %s already %s, skipping", job_id, job.status)
        return False
    return True


def _mark_running(db, job: Job) -> None:
    """Transition the job to running and bump attempts."""
    job.status = JobStatus.running.value
    job.attempts += 1
    job.updated_at = utcnow()
    db.commit()
    _emit(job, "running")
    log.info(
        "running job %s type=%s attempt=%s/%s",
        job.id,
        job.type,
        job.attempts,
        job.max_attempts,
        extra={"job_id": job.id},
    )


def _run_and_finalize(db, job: Job) -> None:
    """Execute the handler and record success, retry, or dead."""
    payload = json.loads(job.payload or "{}")
    started = time.perf_counter()
    try:
        result = run_handler(job.type, payload)
        _succeed(db, job, result, time.perf_counter() - started)
    except Exception as exc:
        _fail(db, job, str(exc), time.perf_counter() - started)


def _succeed(db, job: Job, result: dict, duration: float) -> None:
    """Persist a successful result and emit metrics/events."""
    job.status = JobStatus.succeeded.value
    job.result = json.dumps(result)
    job.error = None
    job.updated_at = utcnow()
    db.commit()
    JOBS_SUCCEEDED.labels(type=job.type).inc()
    JOB_DURATION.labels(type=job.type, status="succeeded").observe(duration)
    log.info("job %s succeeded", job.id, extra={"job_id": job.id})
    _emit(job, "succeeded")


def _fail(db, job: Job, error_msg: str, duration: float) -> None:
    """Retry with backoff or move the job to the DLQ."""
    log.exception("job %s failed: %s", job.id, error_msg, extra={"job_id": job.id})
    JOB_DURATION.labels(type=job.type, status="failed").observe(duration)
    if job.attempts < job.max_attempts:
        _requeue(db, job, error_msg)
    else:
        _dead(db, job, error_msg)


def _requeue(db, job: Job, error_msg: str) -> None:
    """Return the job to queued and push it back onto Redis."""
    job.status = JobStatus.queued.value
    job.error = error_msg
    job.updated_at = utcnow()
    db.commit()
    JOBS_RETRIED.labels(type=job.type).inc()
    time.sleep(min(2 ** (job.attempts - 1), 8))
    enqueue(job.id, priority=job.priority)
    log.info("job %s re-queued for retry", job.id, extra={"job_id": job.id})
    _emit(job, "retried", error=error_msg)


def _dead(db, job: Job, error_msg: str) -> None:
    """Mark permanent failure and push the dead-letter list."""
    job.status = JobStatus.dead.value
    job.error = error_msg
    job.updated_at = utcnow()
    db.commit()
    push_dlq(job.id)
    JOBS_FAILED.labels(type=job.type).inc()
    JOBS_DEAD.labels(type=job.type).inc()
    log.info(
        "job %s moved to DLQ after %s attempts",
        job.id,
        job.attempts,
        extra={"job_id": job.id},
    )
    _emit(job, "dead", error=error_msg)


def _emit(job: Job, event: str, **extra: object) -> None:
    """Publish a lifecycle event for WebSocket subscribers."""
    publish_event(
        {
            "event": event,
            "job_id": job.id,
            "type": job.type,
            "status": job.status,
            "attempts": job.attempts,
            **extra,
        }
    )
