"""Job CRUD and cancel HTTP routes."""

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.config import get_settings
from app.db import get_db
from app.models import JobStatus
from app.rate_limit import limiter
from app.schemas import JobCreate, JobOut
from app.services import job_service

router = APIRouter(tags=["jobs"])
settings = get_settings()


@router.post(
    "/jobs",
    response_model=JobOut,
    status_code=201,
    dependencies=[Depends(require_api_key)],
)
@limiter.limit(settings.rate_limit)
def create_job(
    request: Request,
    body: JobCreate,
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> JobOut:
    """Enqueue a new job (or return the prior one for the same Idempotency-Key)."""
    return job_service.create_job_row(db, body, idempotency_key)


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    status: JobStatus | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[JobOut]:
    """List recent jobs, newest first."""
    return job_service.list_job_rows(db, status, limit)


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)) -> JobOut:
    """Fetch a single job by id."""
    return job_service.get_job_row(db, job_id)


@router.post(
    "/jobs/{job_id}/cancel",
    response_model=JobOut,
    dependencies=[Depends(require_api_key)],
)
def cancel_job(job_id: str, db: Session = Depends(get_db)) -> JobOut:
    """Cancel a job that is still queued."""
    return job_service.cancel_job_row(db, job_id)
