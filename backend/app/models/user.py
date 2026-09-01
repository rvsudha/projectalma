"""Internal user (attorney) model — backs the auth-guarded UI."""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Room to grow (admin, paralegal, ...). Attorneys can transition lead state.
    role: Mapped[str] = mapped_column(String(32), default="attorney", nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email}>"
