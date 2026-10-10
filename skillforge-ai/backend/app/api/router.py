"""Aggregate API routers."""

from fastapi import APIRouter

from app.api import admin, assessments, auth, competencies, health, learner, learning, profile, skills

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(competencies.router)
api_router.include_router(skills.router)
api_router.include_router(assessments.router)
api_router.include_router(learning.router)
api_router.include_router(admin.router)
api_router.include_router(learner.router)
