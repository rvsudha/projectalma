"""initial schema: users, leads, lead_events

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-31
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="attorney"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "leads",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("resume_key", sa.String(length=1024), nullable=False),
        sa.Column("resume_filename", sa.String(length=512), nullable=False),
        sa.Column("resume_content_type", sa.String(length=255), nullable=False),
        sa.Column("resume_size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("state", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("reached_out_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reached_out_by_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["reached_out_by_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_leads_email", "leads", ["email"])
    op.create_index("ix_leads_state", "leads", ["state"])
    op.create_index("ix_leads_created_at", "leads", ["created_at"])

    op.create_table(
        "lead_events",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("lead_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("message", sa.String(length=512), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_lead_events_lead_id", "lead_events", ["lead_id"])


def downgrade() -> None:
    op.drop_table("lead_events")
    op.drop_index("ix_leads_email", table_name="leads")
    op.drop_index("ix_leads_state", table_name="leads")
    op.drop_index("ix_leads_created_at", table_name="leads")
    op.drop_table("leads")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
