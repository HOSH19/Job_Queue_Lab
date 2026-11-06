"""FastAPI application entrypoint."""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.db import init_db
from app.logging_config import configure_logging
from app.rate_limit import limiter
from app.routers import dlq, health, jobs, metrics_route, ws

configure_logging("api")
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create tables on startup (dev convenience; prefer Alembic in prod)."""
    init_db()
    yield


def create_app() -> FastAPI:
    """Build the configured FastAPI app with routers and middleware."""
    application = FastAPI(title="Job Queue Lab", version="2.0.0", lifespan=lifespan)
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    _add_cors(application)
    _add_request_id(application)
    _include_routers(application)
    return application


def _add_cors(application: FastAPI) -> None:
    """Attach browser CORS policy from settings."""
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _add_request_id(application: FastAPI) -> None:
    """Stamp every response with X-Request-Id."""

    @application.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


def _include_routers(application: FastAPI) -> None:
    """Mount feature routers."""
    application.include_router(health.router)
    application.include_router(metrics_route.router)
    application.include_router(jobs.router)
    application.include_router(dlq.router)
    application.include_router(ws.router)


app = create_app()
