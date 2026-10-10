"""Skill-gap snapshot persistence (Phase 5)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.competency import Competency
    from app.models.user import User


class SkillGapSnapshot(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "skill_gap_snapshots"

    analysis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    required_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    gap: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    priority: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    user: Mapped[User] = relationship()
    competency: Mapped[Competency] = relationship()
