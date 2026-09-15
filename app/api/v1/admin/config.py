"""Admin configuration, model download, and cache management endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.llm_engine import engine_manager
from app.db.writers.config_writer import get_ai_config, update_ai_config
from app.schemas.admin import ConfigResponse, ConfigUpdate
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/admin", tags=["Admin Config"])


@router.get("/config", response_model=ApiResponse[ConfigResponse])
async def read_config(
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ConfigResponse]:
    """Retrieve runtime LLM settings from ai_config table."""
    conf = await get_ai_config(session)
    return ApiResponse(
        success=True,
        data=ConfigResponse(
            default_model=str(conf["default_model"]),
            n_gpu_layers=int(conf["n_gpu_layers"]),
            n_threads=int(conf["n_threads"]),
            n_ctx=int(conf["n_ctx"]),
            updated_at=str(conf["updated_at"]) if conf.get("updated_at") else None,
        ),
    )


@router.patch("/config", response_model=ApiResponse[ConfigResponse])
async def modify_config(
    payload: ConfigUpdate,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ConfigResponse]:
    """Update runtime configuration parameters in database."""
    updated = await update_ai_config(
        session=session,
        default_model=payload.default_model,
        n_gpu_layers=payload.n_gpu_layers,
        n_threads=payload.n_threads,
        n_ctx=payload.n_ctx,
    )
    return ApiResponse(
        success=True,
        data=ConfigResponse(
            default_model=str(updated["default_model"]),
            n_gpu_layers=int(updated["n_gpu_layers"]),
            n_threads=int(updated["n_threads"]),
            n_ctx=int(updated["n_ctx"]),
            updated_at=str(updated["updated_at"]) if updated.get("updated_at") else None,
        ),
    )


@router.post("/models/{model_key}/download", response_model=ApiResponse[dict[str, Any]])
async def download_model(
    model_key: str,
    _: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, Any]]:
    """Trigger background download of a supported GGUF model from HuggingFace."""
    result = engine_manager.trigger_download(model_key)
    return ApiResponse(
        success=True,
        data=result,
    )


@router.post("/models/{model_key}/cache", response_model=ApiResponse[dict[str, Any]])
async def preload_model_cache(
    model_key: str,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, Any]]:
    """Explicitly pre-load a model into RAM."""
    conf = await get_ai_config(session)
    engine_manager.load_model(
        model_key=model_key,
        n_gpu_layers=int(conf.get("n_gpu_layers", 0)),
        n_threads=int(conf.get("n_threads", 4)),
        n_ctx=int(conf.get("n_ctx", 4096)),
    )
    return ApiResponse(
        success=True,
        data={"model_key": model_key, "cached": True, "message": f"Model '{model_key}' successfully loaded into RAM."},
    )


@router.post("/models/{model_key}/reload", response_model=ApiResponse[dict[str, Any]])
async def reload_model_cache(
    model_key: str,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, Any]]:
    """Evict and reload a model in RAM with latest config."""
    conf = await get_ai_config(session)
    engine_manager.reload_model(
        model_key=model_key,
        n_gpu_layers=int(conf.get("n_gpu_layers", 0)),
        n_threads=int(conf.get("n_threads", 4)),
        n_ctx=int(conf.get("n_ctx", 4096)),
    )
    return ApiResponse(
        success=True,
        data={"model_key": model_key, "reloaded": True, "message": f"Model '{model_key}' was reloaded successfully."},
    )


@router.delete("/models/{model_key}/cache", response_model=ApiResponse[dict[str, Any]])
async def evict_model_cache(
    model_key: str,
    _: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, Any]]:
    """Evict a model from RAM cache to free memory."""
    evicted = engine_manager.evict_model(model_key)
    if not evicted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "model_not_in_cache",
                    "message": f"Model '{model_key}' was not found in RAM cache",
                },
            },
        )
    return ApiResponse(
        success=True,
        data={"model_key": model_key, "evicted": True, "message": f"Model '{model_key}' was evicted from RAM cache."},
    )
