"""Health check endpoint."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm_engine import engine_manager
from app.db.session import get_db_session
from app.schemas.common import ApiResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=ApiResponse[dict[str, Any]])
async def health_check(
    session: AsyncSession = Depends(get_db_session),
) -> ApiResponse[dict[str, Any]]:
    """Service liveness and database connectivity probe."""
    db_connected = False
    try:
        res = await session.execute(text("SELECT 1"))
        db_connected = bool(res.scalar() == 1)
    except Exception:
        db_connected = False

    models_info = engine_manager.list_models_on_disk()
    loaded_models = [k for k, v in models_info.items() if v["loaded_in_ram"]]

    return ApiResponse(
        success=True,
        data={
            "status": "healthy" if db_connected else "degraded",
            "database_connected": db_connected,
            "models_loaded_in_ram": loaded_models,
            "models_available_on_disk": [k for k, v in models_info.items() if v["exists_on_disk"]],
        },
    )
