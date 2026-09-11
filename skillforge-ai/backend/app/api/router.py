"""Aggregate API routers."""

from fastapi import APIRouter

from app.api import admin, auth, health, learner

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(learner.router)
