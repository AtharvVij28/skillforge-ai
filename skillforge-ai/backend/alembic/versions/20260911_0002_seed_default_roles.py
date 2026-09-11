"""seed default LEARNER and ADMIN roles

Revision ID: 20260911_0002
Revises: 20260911_0001
Create Date: 2026-09-11
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260911_0002"
down_revision: Union[str, None] = "20260911_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO roles (id, code, name, description, created_at, updated_at)
        SELECT gen_random_uuid(), 'LEARNER', 'Learner', 'Standard learner account', NOW(), NOW()
        WHERE NOT EXISTS (SELECT 1 FROM roles WHERE code = 'LEARNER');
        """
    )
    op.execute(
        """
        INSERT INTO roles (id, code, name, description, created_at, updated_at)
        SELECT gen_random_uuid(), 'ADMIN', 'Administrator', 'Platform administrator', NOW(), NOW()
        WHERE NOT EXISTS (SELECT 1 FROM roles WHERE code = 'ADMIN');
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE code IN ('LEARNER', 'ADMIN');")
