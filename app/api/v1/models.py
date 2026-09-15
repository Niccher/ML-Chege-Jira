"""Models discovery endpoint."""

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import verify_api_key
from app.core.llm_engine import engine_manager
from app.schemas.common import ApiResponse

router = APIRouter(tags=["Models"])


@router.get("/models", response_model=ApiResponse[dict[str, Any]])
async def list_models(_: str = Depends(verify_api_key)) -> ApiResponse[dict[str, Any]]:
    """List all supported GGUF model files and their caching status."""
    models = engine_manager.list_models_on_disk()
    return ApiResponse(
        success=True,
        data={
            "models": models,
            "count": len(models),
        },
    )
