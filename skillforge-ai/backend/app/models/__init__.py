"""ORM models package — import all models so metadata is registered."""

from app.models.assessment import (
    Assessment,
    AssessmentAnswer,
    AssessmentAttempt,
    AssessmentQuestion,
    Question,
)
from app.models.audit import AuditLog
from app.models.competency import (
    Competency,
    CompetencyCategory,
    RoleCompetency,
    UserCompetency,
)
from app.models.document import Document, DocumentChunk
from app.models.learning import (
    LearningHistory,
    LearningResource,
    LearningResourceCompetency,
    Recommendation,
)
from app.models.skill_gap import SkillGapSnapshot
from app.models.user import Department, EmailVerificationToken, PasswordResetToken, Role, User, UserProfile

__all__ = [
    "Role",
    "Department",
    "User",
    "UserProfile",
    "EmailVerificationToken",
    "PasswordResetToken",
    "AuditLog",
    "CompetencyCategory",
    "Competency",
    "RoleCompetency",
    "UserCompetency",
    "SkillGapSnapshot",
    "LearningResource",
    "LearningResourceCompetency",
    "LearningHistory",
    "Recommendation",
    "Document",
    "DocumentChunk",
    "Question",
    "Assessment",
    "AssessmentQuestion",
    "AssessmentAttempt",
    "AssessmentAnswer",
]
