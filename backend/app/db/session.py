"""Async database engine and session management."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def _engine_kwargs() -> dict:
    if settings.is_sqlite:
        from sqlalchemy.pool import StaticPool

        return {
            "echo": settings.db_echo,
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False},
        }

    connect_args: dict = {}
    if settings.db_statement_timeout_ms and "asyncpg" in settings.database_url:
        # asyncpg server settings; applied per connection.
        connect_args["server_settings"] = {
            "statement_timeout": str(settings.db_statement_timeout_ms)
        }
    return {
        "echo": settings.db_echo,
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_timeout": settings.db_pool_timeout_seconds,
        "pool_recycle": settings.db_pool_recycle_seconds,
        "pool_pre_ping": True,
        "connect_args": connect_args,
    }


engine = create_async_engine(settings.database_url, **_engine_kwargs())

SessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yields a session, commits on success, rolls back on error."""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
