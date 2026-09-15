"""Admin telemetry endpoint."""

from typing import Any

import fastapi
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.config import settings
from app.core.llm_engine import engine_manager
from app.core.telemetry import get_system_telemetry
from app.db.writers.config_writer import get_ai_config
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/admin", tags=["Admin Telemetry"])


@router.get("/telemetry", response_model=ApiResponse[dict[str, Any]])
async def get_telemetry(
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, Any]]:
    """Return unified container, LLM runtime, model cache, and DB metrics for PHP Admin."""
    system_metrics = get_system_telemetry()
    models_status = engine_manager.list_models_on_disk()

    # Read current DB config
    ai_conf = await get_ai_config(session)

    # Check DB connectivity & table existence
    db_connected = False
    ai_tables_present = False
    try:
        res = await session.execute(text("SHOW TABLES LIKE 'ai_%'"))
        rows = res.fetchall()
        db_connected = True
        ai_tables_present = len(rows) >= 4
    except Exception:
        db_connected = False
        ai_tables_present = False

    try:
        import llama_cpp  # type: ignore

        llama_version = getattr(llama_cpp, "__version__", "0.2.79")
    except Exception:
        llama_version = "N/A"

    runtime_metrics = {
        "llama_cpp_version": llama_version,
        "fastapi_version": fastapi.__version__,
        "default_model": ai_conf.get("default_model", settings.DEFAULT_MODEL),
        "n_gpu_layers": ai_conf.get("n_gpu_layers", settings.N_GPU_LAYERS),
        "n_threads": ai_conf.get("n_threads", settings.N_THREADS),
        "n_ctx": ai_conf.get("n_ctx", settings.N_CTX),
        "compute_mode": "GPU" if ai_conf.get("n_gpu_layers", 0) != 0 else "CPU",
    }

    db_metrics = {
        "connected": db_connected,
        "host": settings.DB_HOST,
        "database": settings.DB_NAME,
        "ai_tables_present": ai_tables_present,
    }

    return ApiResponse(
        success=True,
        data={
            "container": system_metrics,
            "llm_runtime": runtime_metrics,
            "models": models_status,
            "database": db_metrics,
        },
    )
