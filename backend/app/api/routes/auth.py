from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from app.api.deps import CurrentUser, DbSession, rate_limit
from app.core.config import settings
from app.core.errors import AuthenticationError, ForbiddenError
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.services import users

router = APIRouter(prefix="/auth", tags=["auth"])

_login_rate_limit = rate_limit(
    "login",
    limit=lambda: settings.rate_limit_login_per_15min,
    window_seconds=15 * 60,
)
_signup_rate_limit = rate_limit(
    "signup",
    limit=lambda: settings.rate_limit_signup_per_hour,
    window_seconds=60 * 60,
)


def _token_for(user_id: str, role: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user_id, extra_claims={"role": role}),
        expires_in=settings.access_token_expire_minutes * 60,
        role="attorney" if role == "attorney" else "applicant",
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in (attorney or applicant)",
    dependencies=[Depends(_login_rate_limit)],
)
async def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    user = await users.authenticate(db, email=payload.email, password=payload.password)
    if user is None:
        raise AuthenticationError("Incorrect email or password")
    return _token_for(str(user.id), user.role)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Sign up as an applicant, or as an attorney with an invite code",
    dependencies=[Depends(_signup_rate_limit)],
)
async def register(payload: RegisterRequest, db: DbSession) -> TokenResponse:
    if payload.role == "attorney":
        if not settings.attorney_signup_enabled:
            raise ForbiddenError("Attorney sign-up is currently disabled")
        if not payload.invite_code or not secrets.compare_digest(
            payload.invite_code, settings.attorney_signup_code
        ):
            raise ForbiddenError("Invalid invite code")

    user = await users.create_user(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role,
    )
    await db.commit()
    return _token_for(str(user.id), user.role)


@router.get("/me", response_model=UserRead, summary="Current authenticated user")
async def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
