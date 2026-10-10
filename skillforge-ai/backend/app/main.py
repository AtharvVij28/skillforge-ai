"""SkillForge AI — FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings, settings
from app.core.database import get_session_factory, reset_db_state
from app.services.auth_service import bootstrap_admin_if_configured
from app.services.catalog_seed import ensure_learning_catalog
from app.services.framework_seed import ensure_competency_framework
from app.services.role_service import ensure_default_roles


def _startup_seed() -> None:
    cfg = get_settings()
    if not cfg.has_database_credentials:
        return
    try:
        session_factory = get_session_factory()
        db = session_factory()
        try:
            ensure_default_roles(db)
            ensure_competency_framework(db)
            ensure_learning_catalog(db)
            if (
                cfg.is_development
                and cfg.bootstrap_admin_email
                and cfg.bootstrap_admin_password
            ):
                bootstrap_admin_if_configured(
                    db,
                    cfg.bootstrap_admin_email,
                    cfg.bootstrap_admin_password,
                )
        finally:
            db.close()
    except Exception:
        # Startup must not crash the API if DB is temporarily unavailable.
        reset_db_state()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _startup_seed()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.api_prefix)

    @application.get("/", tags=["root"])
    def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "status": "ok",
            "phase": "8",
            "docs": "/docs",
        }

    return application


app = create_app()
