"""Prometheus scrape endpoint."""

from fastapi import APIRouter
from fastapi.responses import Response

from app.metrics import QUEUE_DEPTH, metrics_payload
from app.queue import queue_depth

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def metrics() -> Response:
    """Expose Prometheus text metrics, refreshing queue depth first."""
    try:
        QUEUE_DEPTH.set(queue_depth())
    except Exception:
        pass
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)
