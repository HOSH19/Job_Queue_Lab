"""Live job events over WebSocket."""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import get_settings
from app.queue import get_redis

router = APIRouter(tags=["ws"])
log = logging.getLogger("api")


@router.websocket("/ws/jobs")
async def jobs_ws(websocket: WebSocket) -> None:
    """Forward Redis pub/sub job events to the browser."""
    await websocket.accept()
    settings = get_settings()
    pubsub = get_redis().pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(settings.events_channel)
    try:
        await _pump(websocket, pubsub)
    except WebSocketDisconnect:
        pass
    except Exception:
        log.exception("websocket /ws/jobs ended with error")
    finally:
        _close_pubsub(pubsub, settings.events_channel)


async def _pump(websocket: WebSocket, pubsub: object) -> None:
    """Read Redis messages and send them as WebSocket text frames."""
    while True:
        message = await asyncio.to_thread(pubsub.get_message, timeout=1.0)
        if not message or message.get("type") != "message":
            continue
        data = message.get("data")
        if isinstance(data, bytes):
            data = data.decode()
        await websocket.send_text(str(data))


def _close_pubsub(pubsub: object, channel: str) -> None:
    """Best-effort unsubscribe and close."""
    try:
        pubsub.unsubscribe(channel)
        pubsub.close()
    except Exception:
        pass
