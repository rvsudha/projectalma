"""User lookup, authentication, and the seed-attorney bootstrap."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import ConflictError
from app.core.logging import get_logger
from app.core.security import hash_password, verify_password
from app.models.user import User

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _dummy_hash() -> str:
    # A real hash to verify against when the user does not exist, so a missing
    # account and a wrong password cost roughly the same (anti-enumeration).
    return hash_password("not-a-real-password")


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == email.lower()))


async def authenticate(db: AsyncSession, *, email: str, password: str) -> User | None:
    user = await get_by_email(db, email)
    if user is None:
        verify_password(password, _dummy_hash())
        return None
    if not user.is_active or not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(
    db: AsyncSession, *, email: str, password: str, full_name: str, role: str
) -> User:
    """Create a new active account. Raises ConflictError on a duplicate email."""
    email = email.lower()
    if await get_by_email(db, email) is not None:
        raise ConflictError("An account with that email already exists")
    user = User(
        email=email,
        full_name=full_name.strip(),
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    logger.info("user registered", extra={"email": email, "role": role})
    return user


async def ensure_seed_attorney(db: AsyncSession) -> None:
    """Idempotently create the configured seed attorney account."""
    email = settings.seed_attorney_email.lower()
    if await get_by_email(db, email) is not None:
        return
    db.add(
        User(
            email=email,
            full_name=settings.seed_attorney_name,
            hashed_password=hash_password(settings.seed_attorney_password),
            role="attorney",
            is_active=True,
        )
    )
    await db.commit()
    logger.info("seed attorney created", extra={"email": email})
