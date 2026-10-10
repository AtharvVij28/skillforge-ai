"""add skill_gap_snapshots

Revision ID: 20260919_0003
Revises: 20260911_0002
Create Date: 2026-09-19
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260919_0003"
down_revision: Union[str, None] = "20260911_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE skill_gap_snapshots (
            id UUID NOT NULL,
            analysis_id UUID NOT NULL,
            user_id UUID NOT NULL,
            competency_id UUID NOT NULL,
            job_role VARCHAR(255),
            current_score NUMERIC(5, 2) NOT NULL,
            required_score NUMERIC(5, 2) NOT NULL,
            gap NUMERIC(5, 2) NOT NULL,
            priority VARCHAR(16) NOT NULL,
            confidence NUMERIC(5, 2) NOT NULL,
            source VARCHAR(32) NOT NULL,
            explanation TEXT NOT NULL,
            computed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY(competency_id) REFERENCES competencies (id) ON DELETE CASCADE
        );
        """
    )
    op.execute("CREATE INDEX ix_skill_gap_snapshots_analysis_id ON skill_gap_snapshots (analysis_id);")
    op.execute("CREATE INDEX ix_skill_gap_snapshots_user_id ON skill_gap_snapshots (user_id);")
    op.execute("CREATE INDEX ix_skill_gap_snapshots_competency_id ON skill_gap_snapshots (competency_id);")
    op.execute("CREATE INDEX ix_skill_gap_snapshots_computed_at ON skill_gap_snapshots (computed_at);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS skill_gap_snapshots CASCADE")
