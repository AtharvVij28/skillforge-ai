"""Identity and profile models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.assessment import Assessment, AssessmentAttempt
    from app.models.audit import AuditLog
    from app.models.competency import RoleCompetency, UserCompetency
    from app.models.document import Document
    from app.models.learning import LearningHistory, Recommendation


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    users: Mapped[list[User]] = relationship(back_populates="role")


class Department(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "departments"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    users: Mapped[list[User]] = relationship(back_populates="department")
    role_competencies: Mapped[list[RoleCompetency]] = relationship(back_populates="department")


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    role: Mapped[Role] = relationship(back_populates="users")
    department: Mapped[Optional[Department]] = relationship(back_populates="users")
    profile: Mapped[Optional[UserProfile]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    competencies: Mapped[list[UserCompetency]] = relationship(back_populates="user")
    learning_history: Mapped[list[LearningHistory]] = relationship(back_populates="user")
    recommendations: Mapped[list[Recommendation]] = relationship(back_populates="user")
    assessment_attempts: Mapped[list[AssessmentAttempt]] = relationship(back_populates="user")
    documents: Mapped[list[Document]] = relationship(back_populates="uploaded_by_user")
    created_assessments: Mapped[list[Assessment]] = relationship(back_populates="created_by_user")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="user")


class UserProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    designation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    job_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    assignment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    education: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    technical_skills: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    statistical_skills: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    digital_skills: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    managerial_skills: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    behavioural_skills: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    previous_training: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    career_goals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    profile_completion_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped[User] = relationship(back_populates="profile")
