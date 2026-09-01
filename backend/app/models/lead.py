"""Lead model — a public prospect submission plus its internal review state."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.lead_event import LeadEvent


class LeadState(str, enum.Enum):
    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"


# Human-readable "current milestone" shown on both dashboards, derived from state.
LEAD_MILESTONE: dict[LeadState, str] = {
    LeadState.PENDING: "Awaiting attorney review",
    LeadState.REACHED_OUT: "Attorney has reached out",
}


class Lead(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "leads"

    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)

    # Storage key (path/object name) resolvable by the configured StorageBackend.
    resume_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    resume_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    resume_content_type: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_size_bytes: Mapped[int] = mapped_column(nullable=False, default=0)

    state: Mapped[LeadState] = mapped_column(
        Enum(LeadState, native_enum=False, length=32),
        default=LeadState.PENDING,
        nullable=False,
        index=True,
    )

    # Denormalised audit of the latest PENDING -> REACHED_OUT transition.
    reached_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reached_out_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    events: Mapped[list[LeadEvent]] = relationship(
        back_populates="lead",
        cascade="all, delete-orphan",
        order_by="LeadEvent.created_at",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Lead {self.email} {self.state}>"
