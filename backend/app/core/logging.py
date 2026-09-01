"""Structured JSON logging with request-id correlation."""

from __future__ import annotations

import logging
import sys

try:  # package layout changed in python-json-logger 3.1
    from pythonjsonlogger.json import JsonFormatter
except ImportError:  # pragma: no cover
    from pythonjsonlogger.jsonlogger import JsonFormatter

from app.core.config import settings
from app.core.context import get_request_id

_CONFIGURED = False


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def configure_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(_RequestIdFilter())
    handler.setFormatter(
        JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
            rename_fields={"asctime": "timestamp", "levelname": "level"},
            timestamp=True,
        )
    )

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    for noisy, level in (
        ("uvicorn.access", logging.WARNING),
        ("uvicorn.error", logging.INFO),
        ("sqlalchemy.engine", logging.WARNING),
        ("aiosqlite", logging.WARNING),
        ("asyncio", logging.WARNING),
        ("urllib3", logging.WARNING),
        ("httpx", logging.WARNING),
        ("httpcore", logging.WARNING),
        # passlib probes bcrypt's version in a way that trips a benign
        # AttributeError log on bcrypt 4.x — hashing itself works.
        ("passlib", logging.ERROR),
    ):
        logging.getLogger(noisy).setLevel(level)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
