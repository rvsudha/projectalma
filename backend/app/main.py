"""FastAPI application factory and lifespan wiring."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import RequestContextMiddleware
from app.api.routes import api_router
from app.core.config import settings
from app.core.errors import install_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.session import SessionLocal, engine
from app.schemas.common import ErrorResponse
from app.services.users import ensure_seed_attorney

logger = get_logger(__name__)

_TAGS_METADATA = [
    {"name": "leads", "description": "Public lead intake and the internal attorney dashboard."},
    {"name": "portal", "description": "Applicant self-service — read-only view of your own cases."},
    {"name": "auth", "description": "Login and sign-up (applicant or attorney), JWT bearer."},
    {"name": "meta", "description": "Liveness and readiness probes."},
]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info(
        "starting",
        extra={"project": settings.project_name, "env": settings.environment},
    )
    if not settings.is_testing:
        async with SessionLocal() as db:
            await ensure_seed_attorney(db)
    yield
    await engine.dispose()
    logger.info("shutdown complete")


def create_app() -> FastAPI:
    show_docs = settings.docs_enabled and settings.environment != "production"
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        description="Lead management API — public intake, attorney review, audit trail.",
        lifespan=lifespan,
        openapi_tags=_TAGS_METADATA,
        docs_url="/docs" if show_docs else None,
        redoc_url="/redoc" if show_docs else None,
        openapi_url="/openapi.json" if show_docs else None,
        responses={
            400: {"model": ErrorResponse},
            401: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
            429: {"model": ErrorResponse},
        },
    )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    install_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
