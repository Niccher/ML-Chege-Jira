"""API v1 master router aggregating all domain and admin routes."""

from fastapi import APIRouter

from app.api.v1.admin.config import router as admin_config_router
from app.api.v1.admin.telemetry import router as admin_telemetry_router
from app.api.v1.health import router as health_router
from app.api.v1.models import router as models_router
from app.api.v1.resources.projects import router as projects_router
from app.api.v1.resources.qa import router as qa_router
from app.api.v1.resources.sprints import router as sprints_router
from app.api.v1.resources.tasks import router as tasks_router
from app.api.v1.resources.time_reports import router as time_reports_router
from app.api.v1.resources.background_tasks import router as background_tasks_router

v1_router = APIRouter(prefix="/api/v1")

# Health & Models
v1_router.include_router(health_router)
v1_router.include_router(models_router)

# Admin routes
v1_router.include_router(admin_telemetry_router)
v1_router.include_router(admin_config_router)

# Resource routes
v1_router.include_router(tasks_router)
v1_router.include_router(sprints_router)
v1_router.include_router(projects_router)
v1_router.include_router(time_reports_router)
v1_router.include_router(qa_router)
v1_router.include_router(background_tasks_router)
