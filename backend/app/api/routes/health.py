from __future__ import annotations

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.api.deps import DbSession

router = APIRouter(tags=["meta"])


@router.get("/health", summary="Liveness probe")
async def health() -> dict[str, str]:
    """Process is up. Does not touch dependencies."""
    return {"status": "ok"}


@router.get("/ready", summary="Readiness probe")
async def ready(db: DbSession, response: Response) -> dict[str, str]:
    """Ready to serve traffic — verifies the database is reachable."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable", "database": "down"}
    return {"status": "ok", "database": "up"}
