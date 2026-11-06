"""Prometheus metrics for the job queue."""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

JOBS_ENQUEUED = Counter("jobqueue_jobs_enqueued_total", "Jobs accepted by the API", ["type"])
JOBS_SUCCEEDED = Counter("jobqueue_jobs_succeeded_total", "Jobs that succeeded", ["type"])
JOBS_FAILED = Counter("jobqueue_jobs_failed_total", "Jobs that permanently failed", ["type"])
JOBS_RETRIED = Counter("jobqueue_jobs_retried_total", "Jobs re-queued after failure", ["type"])
JOBS_DEAD = Counter("jobqueue_jobs_dead_total", "Jobs moved to the dead-letter queue", ["type"])
JOB_DURATION = Histogram(
    "jobqueue_job_duration_seconds",
    "Handler wall time",
    ["type", "status"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30),
)
QUEUE_DEPTH = Gauge("jobqueue_queue_depth", "Ready + delayed jobs in Redis")


def metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
