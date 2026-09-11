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
from app.models.user import Department, Role, User, UserProfile

__all__ = [
    "Role",
    "Department",
    "User",
    "UserProfile",
    "AuditLog",
    "CompetencyCategory",
    "Competency",
    "RoleCompetency",
    "UserCompetency",
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
