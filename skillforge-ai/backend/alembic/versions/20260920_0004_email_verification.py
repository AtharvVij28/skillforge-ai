"""add email verification

Revision ID: 20260920_0004
Revises: 20260919_0003
Create Date: 2026-09-20
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260920_0004"
down_revision: Union[str, None] = "20260919_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE")
    op.execute("UPDATE users SET email_verified_at = NOW() WHERE email_verified_at IS NULL")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS email_verification_tokens (
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
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_email_verification_tokens_token_hash "
        "ON email_verification_tokens (token_hash);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_email_verification_tokens_user_id "
        "ON email_verification_tokens (user_id);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS email_verification_tokens CASCADE")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS email_verified_at")
