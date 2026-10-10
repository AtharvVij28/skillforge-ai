"""add password reset tokens

Revision ID: 20260921_0005
Revises: 20260920_0004
Create Date: 2026-09-21
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260921_0005"
down_revision: Union[str, None] = "20260920_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id UUID NOT NULL,
            user_id UUID NOT NULL,
            token_hash VARCHAR(64) NOT NULL,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            used_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_password_reset_tokens_token_hash "
        "ON password_reset_tokens (token_hash);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_user_id ON password_reset_tokens (user_id);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS password_reset_tokens CASCADE")
