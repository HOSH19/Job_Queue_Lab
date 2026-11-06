"""Structured logging setup for API and worker."""

from __future__ import annotations

import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from app.config import get_settings


def configure_logging(service: str) -> None:
    settings = get_settings()
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    if settings.log_json:
        formatter = JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level"},
        )
        handler.setFormatter(formatter)
    else:
        handler.setFormatter(
            logging.Formatter(f"%(asctime)s %(levelname)s [{service}] %(message)s")
        )
    root.addHandler(handler)
    root.setLevel(logging.INFO)
