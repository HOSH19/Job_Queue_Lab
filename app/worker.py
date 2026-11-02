"""Redis BRPOP worker: claim jobs, run handlers, retry on failure."""

from __future__ import annotations

import json
import logging
import signal
import sys
import time

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.jobs.handlers import run_handler
from app.models import Job, JobStatus, utcnow
from app.queue import dequeue, enqueue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [worker] %(message)s",
)
log = logging.getLogger("worker")

_running = True


def _handle_signal(signum: int, _frame: object) -> None:
    global _running
    log.info("received signal %s, shutting down after current job", signum)
    _running = False


def process_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if job is None:
            log.warning("job %s not found in DB, skipping", job_id)
            return

        if job.status == JobStatus.cancelled.value:
            log.info("job %s cancelled, skipping", job_id)
            return

        if job.status not in (JobStatus.queued.value, JobStatus.running.value):
            log.info("job %s already %s, skipping", job_id, job.status)
            return

        job.status = JobStatus.running.value
        job.attempts += 1
        job.updated_at = utcnow()
        db.commit()

        payload = json.loads(job.payload or "{}")
        log.info("running job %s type=%s attempt=%s/%s", job.id, job.type, job.attempts, job.max_attempts)

        try:
            result = run_handler(job.type, payload)
            job.status = JobStatus.succeeded.value
            job.result = json.dumps(result)
            job.error = None
            job.updated_at = utcnow()
            db.commit()
            log.info("job %s succeeded", job.id)
        except Exception as exc:
            error_msg = str(exc)
            log.exception("job %s failed: %s", job.id, error_msg)
            if job.attempts < job.max_attempts:
                job.status = JobStatus.queued.value
                job.error = error_msg
                job.updated_at = utcnow()
                db.commit()
                # Brief backoff before re-queue so bursts don't spin.
                time.sleep(min(2 ** (job.attempts - 1), 8))
                enqueue(job.id)
                log.info("job %s re-queued for retry", job.id)
            else:
                job.status = JobStatus.failed.value
                job.error = error_msg
                job.updated_at = utcnow()
                db.commit()
                log.info("job %s permanently failed after %s attempts", job.id, job.attempts)
    finally:
        db.close()


def main() -> None:
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    settings = get_settings()
    init_db()
    log.info("worker started queue=%s max_attempts_default=%s", settings.queue_key, settings.max_attempts)

    while _running:
        try:
            job_id = dequeue(timeout=2)
        except Exception:
            log.exception("dequeue failed; sleeping briefly")
            time.sleep(1)
            continue

        if job_id is None:
            continue

        try:
            process_job(job_id)
        except Exception:
            log.exception("unexpected error processing %s", job_id)

    log.info("worker stopped")


if __name__ == "__main__":
    main()
    sys.exit(0)
