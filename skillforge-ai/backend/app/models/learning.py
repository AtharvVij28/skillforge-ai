"""Learning resource and recommendation models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.competency import Competency
    from app.models.user import User


class LearningResource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "learning_resources"

    external_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    estimated_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_json: Mapped[Optional[Any]] = mapped_column("metadata", JSONB, nullable=True)

    competency_links: Mapped[list[LearningResourceCompetency]] = relationship(
        back_populates="resource", cascade="all, delete-orphan"
    )
    learning_history: Mapped[list[LearningHistory]] = relationship(back_populates="resource")
    recommendations: Mapped[list[Recommendation]] = relationship(back_populates="resource")


class LearningResourceCompetency(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "learning_resource_competencies"
    __table_args__ = (
        UniqueConstraint("resource_id", "competency_id", name="uq_resource_competency"),
    )

    resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_resources.id", ondelete="CASCADE"),
        nullable=False,
    )
    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
    )
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("1.00"), nullable=False)

    resource: Mapped[LearningResource] = relationship(back_populates="competency_links")
    competency: Mapped[Competency] = relationship(back_populates="resource_links")


class LearningHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "learning_history"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(32), default="RECOMMENDED", nullable=False)
    progress_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship(back_populates="learning_history")
    resource: Mapped[LearningResource] = relationship(back_populates="learning_history")


class Recommendation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "recommendations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_resources.id", ondelete="CASCADE"),
        nullable=False,
    )
    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
    )
    relevance_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    gap_at_generation: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    expected_benefit: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_effort_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    rank: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="recommendations")
    resource: Mapped[LearningResource] = relationship(back_populates="recommendations")
    competency: Mapped[Competency] = relationship(back_populates="recommendations")
