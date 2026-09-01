"""Lead business logic — HTTP-agnostic, async."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.errors import ConflictError, NotFoundError, UnsupportedMediaTypeError
from app.core.logging import get_logger
from app.models.lead import Lead, LeadState
from app.models.lead_event import LeadEvent, LeadEventType
from app.models.user import User
from app.schemas.lead import LeadCreate
from app.services.storage import StoredFile, get_storage, sniff_matches

logger = get_logger(__name__)

# Allowed state transitions. Both directions are permitted: an attorney who marks
# a lead REACHED_OUT by mistake can reopen it. Every move is written as its own
# append-only audit event, so the full history stays visible either way.
_TRANSITIONS: dict[LeadState, set[LeadState]] = {
    LeadState.PENDING: {LeadState.REACHED_OUT},
    LeadState.REACHED_OUT: {LeadState.PENDING},
}


def _record_event(
    db: AsyncSession,
    lead: Lead,
    *,
    type_: LeadEventType,
    message: str,
    actor_id: uuid.UUID | None = None,
) -> None:
    """Append an audit event without touching the (lazy) ``lead.events`` collection."""
    db.add(LeadEvent(lead_id=lead.id, type=type_, message=message, actor_id=actor_id))


async def create_lead(
    db: AsyncSession,
    *,
    payload: LeadCreate,
    resume_bytes: bytes,
    resume_filename: str,
    resume_content_type: str,
) -> Lead:
    if not sniff_matches(resume_content_type, resume_bytes):
        raise UnsupportedMediaTypeError(
            "Resume file contents do not match a supported document type (PDF, DOC, DOCX)."
        )

    stored: StoredFile = await get_storage().save(
        data=resume_bytes,
        filename=resume_filename,
        content_type=resume_content_type,
    )
    lead = Lead(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=str(payload.email).lower(),
        resume_key=stored.key,
        resume_filename=stored.filename,
        resume_content_type=stored.content_type,
        resume_size_bytes=stored.size,
        state=LeadState.PENDING,
    )
    db.add(lead)
    await db.flush()  # populate lead.id before referencing it from the event
    _record_event(db, lead, type_=LeadEventType.CREATED, message="Lead submitted")
    await db.flush()
    logger.info("lead created", extra={"lead_id": str(lead.id)})
    return lead


async def get_lead(db: AsyncSession, lead_id: uuid.UUID) -> Lead:
    lead = await db.get(Lead, lead_id)
    if lead is None:
        raise NotFoundError("Lead not found")
    return lead


async def list_lead_events(db: AsyncSession, lead_id: uuid.UUID) -> list[LeadEvent]:
    rows = await db.scalars(
        select(LeadEvent).where(LeadEvent.lead_id == lead_id).order_by(LeadEvent.created_at.asc())
    )
    return list(rows.all())


async def list_leads_for_email(db: AsyncSession, email: str) -> list[Lead]:
    """Every lead submitted with this email address (a prospect's own cases)."""
    rows = await db.scalars(
        select(Lead).where(Lead.email == email.lower()).order_by(Lead.created_at.desc())
    )
    return list(rows.all())


async def stats(db: AsyncSession) -> dict[str, int]:
    """Aggregate counts for the dashboard summary tiles."""
    rows = await db.execute(select(Lead.state, func.count()).group_by(Lead.state))
    by_state: dict[LeadState, int] = {state: n for state, n in rows.all()}  # noqa: C416
    pending = by_state.get(LeadState.PENDING, 0)
    reached = by_state.get(LeadState.REACHED_OUT, 0)
    return {"total": pending + reached, "pending": pending, "reached_out": reached}


async def list_activity(db: AsyncSession, *, limit: int = 20) -> list[dict]:
    """Recent events across all leads, with lead + actor names, newest first."""
    actor = aliased(User)
    rows = await db.execute(
        select(
            LeadEvent.id,
            LeadEvent.lead_id,
            LeadEvent.type,
            LeadEvent.message,
            LeadEvent.created_at,
            Lead.first_name,
            Lead.last_name,
            actor.full_name,
        )
        .join(Lead, Lead.id == LeadEvent.lead_id)
        .join(actor, actor.id == LeadEvent.actor_id, isouter=True)
        .order_by(LeadEvent.created_at.desc())
        .limit(limit)
    )
    return [
        {
            "id": r.id,
            "lead_id": r.lead_id,
            "lead_name": f"{r.first_name} {r.last_name}",
            "type": r.type,
            "message": r.message,
            "actor_name": r.full_name,
            "created_at": r.created_at,
        }
        for r in rows.all()
    ]


async def list_leads(
    db: AsyncSession,
    *,
    state: LeadState | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Lead], int]:
    filters = []
    if state is not None:
        filters.append(Lead.state == state)
    if search:
        term = f"%{search.strip().lower()}%"
        filters.append(
            func.lower(Lead.first_name).like(term)
            | func.lower(Lead.last_name).like(term)
            | func.lower(Lead.email).like(term)
        )

    base = select(Lead).where(*filters)
    total = await db.scalar(select(func.count()).select_from(base.subquery()))
    rows = await db.scalars(base.order_by(Lead.created_at.desc()).limit(limit).offset(offset))
    return list(rows.all()), int(total or 0)


async def update_lead_state(
    db: AsyncSession, *, lead_id: uuid.UUID, new_state: LeadState, actor: User
) -> Lead:
    lead = await get_lead(db, lead_id)
    if new_state == lead.state:
        return lead
    if new_state not in _TRANSITIONS[lead.state]:
        raise ConflictError(f"Cannot move lead from {lead.state.value} to {new_state.value}")

    previous = lead.state
    lead.state = new_state
    message = f"{previous.value} -> {new_state.value}"
    if new_state == LeadState.REACHED_OUT:
        lead.reached_out_at = datetime.now(UTC)
        lead.reached_out_by_id = actor.id
    else:  # REACHED_OUT -> PENDING: attorney reopened the lead
        lead.reached_out_at = None
        lead.reached_out_by_id = None
        message += " (reopened)"
    _record_event(
        db,
        lead,
        type_=LeadEventType.STATE_CHANGED,
        message=message,
        actor_id=actor.id,
    )
    await db.flush()
    logger.info(
        "lead state changed",
        extra={"lead_id": str(lead.id), "from": previous.value, "to": new_state.value},
    )
    return lead
