"""Competency framework models."""

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
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.assessment import Question
    from app.models.learning import LearningResourceCompetency, Recommendation
    from app.models.user import Department, User


class CompetencyCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "competency_categories"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    competencies: Mapped[list[Competency]] = relationship(back_populates="category")


class Competency(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "competencies"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competency_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proficiency_levels: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    default_priority: Mapped[str] = mapped_column(String(16), default="MEDIUM", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped[CompetencyCategory] = relationship(back_populates="competencies")
    role_competencies: Mapped[list[RoleCompetency]] = relationship(back_populates="competency")
    user_competencies: Mapped[list[UserCompetency]] = relationship(back_populates="competency")
    resource_links: Mapped[list[LearningResourceCompetency]] = relationship(
        back_populates="competency"
    )
    recommendations: Mapped[list[Recommendation]] = relationship(back_populates="competency")
    questions: Mapped[list[Question]] = relationship(back_populates="competency")


class RoleCompetency(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Required proficiency by job role code (not RBAC role)."""

    __tablename__ = "role_competencies"
    __table_args__ = (
        UniqueConstraint(
            "role_code",
            "department_id",
            "competency_id",
            name="uq_role_department_competency",
        ),
    )

    role_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
    )
    required_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    priority: Mapped[str] = mapped_column(String(16), default="MEDIUM", nullable=False)
    relevance_weight: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("1.00"), nullable=False
    )

    department: Mapped[Optional[Department]] = relationship(back_populates="role_competencies")
    competency: Mapped[Competency] = relationship(back_populates="role_competencies")


class UserCompetency(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_competencies"
    __table_args__ = (UniqueConstraint("user_id", "competency_id", name="uq_user_competency"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), nullable=False
    )
    confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), nullable=False
    )
    source: Mapped[str] = mapped_column(String(32), default="PROFILE", nullable=False)
    last_assessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship(back_populates="competencies")
    competency: Mapped[Competency] = relationship(back_populates="user_competencies")
