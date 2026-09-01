"""Append-only audit trail for everything that happens to a lead."""

from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.lead import Lead


class LeadEventType(str, enum.Enum):
    CREATED = "CREATED"
    STATE_CHANGED = "STATE_CHANGED"
    EMAIL_SENT = "EMAIL_SENT"


class LeadEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "lead_events"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[LeadEventType] = mapped_column(
        Enum(LeadEventType, native_enum=False, length=32), nullable=False
    )
    # Free-form, human-readable summary, e.g. "PENDING -> REACHED_OUT".
    message: Mapped[str] = mapped_column(String(512), nullable=False)
    # Who caused it (an attorney) — null for system/public actions.
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Set in Python (microsecond precision) so the activity feed orders correctly
    # even for events written in the same DB tick; overrides TimestampMixin.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    lead: Mapped[Lead] = relationship(back_populates="events")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<LeadEvent {self.type} lead={self.lead_id}>"
