import json
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db, init_db, ping_db
from app.models import Job, JobStatus, utcnow
from app.queue import enqueue, ping_redis
from app.schemas import HealthOut, JobCreate, JobOut


def _job_to_out(job: Job) -> JobOut:
    return JobOut(
        id=job.id,
        type=job.type,
        payload=json.loads(job.payload or "{}"),
        status=JobStatus(job.status),
        result=json.loads(job.result) if job.result else None,
        error=job.error,
        attempts=job.attempts,
        max_attempts=job.max_attempts,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


settings = get_settings()
app = FastAPI(title="Job Queue Lab", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    redis_ok = ping_redis()
    db_ok = ping_db()
    return HealthOut(
        status="ok" if redis_ok and db_ok else "degraded",
        redis="up" if redis_ok else "down",
        database="up" if db_ok else "down",
    )


@app.post("/jobs", response_model=JobOut, status_code=201)
def create_job(body: JobCreate, db: Session = Depends(get_db)) -> JobOut:
    job_id = str(uuid.uuid4())
    max_attempts = body.max_attempts if body.max_attempts is not None else settings.max_attempts
    job = Job(
        id=job_id,
        type=body.type.value,
        payload=json.dumps(body.payload),
        status=JobStatus.queued.value,
        attempts=0,
        max_attempts=max_attempts,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        enqueue(job_id)
    except Exception as exc:
        job.status = JobStatus.failed.value
        job.error = f"failed to enqueue: {exc}"
        job.updated_at = utcnow()
        db.commit()
        db.refresh(job)
        raise HTTPException(status_code=503, detail=f"Redis enqueue failed: {exc}") from exc

    return _job_to_out(job)


@app.get("/jobs", response_model=list[JobOut])
def list_jobs(
    status: JobStatus | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[JobOut]:
    query = db.query(Job).order_by(Job.created_at.desc())
    if status is not None:
        query = query.filter(Job.status == status.value)
    jobs = query.limit(limit).all()
    return [_job_to_out(j) for j in jobs]


@app.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)) -> JobOut:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return _job_to_out(job)


@app.post("/jobs/{job_id}/cancel", response_model=JobOut)
def cancel_job(job_id: str, db: Session = Depends(get_db)) -> JobOut:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != JobStatus.queued.value:
        raise HTTPException(status_code=409, detail=f"cannot cancel job in status {job.status}")
    job.status = JobStatus.cancelled.value
    job.updated_at = utcnow()
    db.commit()
    db.refresh(job)
    return _job_to_out(job)
