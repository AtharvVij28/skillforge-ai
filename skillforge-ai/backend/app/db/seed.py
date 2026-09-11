"""Seed data entrypoint.

Phase 3: ensures LEARNER/ADMIN roles exist and optionally bootstraps a
development admin from environment variables.

Public registration never creates ADMIN accounts.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.core.database import get_session_factory, reset_db_state
from app.services.auth_service import bootstrap_admin_if_configured
from app.services.role_service import ensure_default_roles


def run_seed() -> None:
    cfg = get_settings()
    if not cfg.has_database_credentials:
        raise RuntimeError(
            "DATABASE_URL still contains a password placeholder. "
            "Configure your local .env before seeding."
        )

    reset_db_state()
    db = get_session_factory()()
    try:
        roles = ensure_default_roles(db)
        print(f"Roles ready: {', '.join(sorted(roles))}")

        if cfg.bootstrap_admin_email and cfg.bootstrap_admin_password:
            if not cfg.is_development:
                raise RuntimeError("Admin bootstrap is only allowed when APP_ENV=development")
            user = bootstrap_admin_if_configured(
                db,
                cfg.bootstrap_admin_email,
                cfg.bootstrap_admin_password,
            )
            if user:
                print(f"Bootstrap admin ready: {user.email} (password not logged)")
        else:
            print(
                "No bootstrap admin created. Set BOOTSTRAP_ADMIN_EMAIL and "
                "BOOTSTRAP_ADMIN_PASSWORD in .env for development admin setup."
            )
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
