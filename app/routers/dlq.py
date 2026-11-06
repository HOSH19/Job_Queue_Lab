"""Dead-letter queue inspection."""

from fastapi import APIRouter, Query

from app.queue import list_dlq
from app.schemas import DlqItem

router = APIRouter(tags=["dlq"])


@router.get("/dlq", response_model=list[DlqItem])
def get_dlq(limit: int = Query(default=50, ge=1, le=200)) -> list[DlqItem]:
    """List recent dead-letter job ids from Redis."""
    return [DlqItem(job_id=jid) for jid in list_dlq(limit)]
