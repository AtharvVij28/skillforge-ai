"""SQLAlchemy engine, session factory, and FastAPI dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings, is_placeholder_database_url


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def create_db_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine. Does not log the connection URL."""
    url = database_url or get_settings().database_url
    return create_engine(
        url,
        pool_pre_ping=True,
        future=True,
    )


def get_engine() -> Engine:
    """Lazy singleton engine for the application process."""
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_db_engine()
        _SessionLocal = sessionmaker(
            bind=_engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=Session,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a request-scoped session."""
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """Return True if a simple SELECT 1 succeeds. Never exposes credentials.

    Always reads current settings via get_settings() so placeholder DATABASE_URL
    values are rejected even if a module-level settings snapshot is stale.
    """
    cfg = get_settings()
    if is_placeholder_database_url(cfg.database_url) or not cfg.has_database_credentials:
        return False
    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def reset_db_state() -> None:
    """Reset cached engine/session (used by tests)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
