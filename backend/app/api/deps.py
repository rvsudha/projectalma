"""Shared FastAPI dependencies."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AuthenticationError, ForbiddenError, RateLimitedError
from app.core.ratelimit import get_rate_limiter
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

DbSession = Annotated[AsyncSession, Depends(get_db)]

_bearer = HTTPBearer(auto_error=False, description="JWT access token")


async def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    if credentials is None:
        raise AuthenticationError("Not authenticated")
    try:
        claims = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(claims["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise AuthenticationError("Could not validate credentials") from exc

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("Could not validate credentials")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_attorney(user: CurrentUser) -> User:
    if user.role != "attorney":
        raise ForbiddenError("This area is for attorneys only")
    return user


CurrentAttorney = Annotated[User, Depends(get_current_attorney)]


def _client_ip(request: Request) -> str:
    # X-Forwarded-For is set by the trusted reverse proxy in front of the app.
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(
    bucket: str, *, limit: int | Callable[[], int], window_seconds: int
) -> Callable[[Request], Awaitable[None]]:
    """Dependency factory: fixed-window limit per client IP for one route.

    ``limit`` may be a callable so it is resolved per request (tests, hot reload).
    """

    async def _dep(request: Request) -> None:
        resolved = limit() if callable(limit) else limit
        key = f"{bucket}:{_client_ip(request)}"
        result = get_rate_limiter().check(key, limit=resolved, window_seconds=window_seconds)
        if not result.allowed:
            raise RateLimitedError(
                "Too many requests. Please try again later.",
                retry_after=result.retry_after,
            )

    return _dep
