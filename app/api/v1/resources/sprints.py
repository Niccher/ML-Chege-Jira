"""Sprint summary REST endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.llm_engine import engine_manager
from app.core.prompt_builder import render_prompt
from app.db.readers.sprint_reader import get_sprint_full_context
from app.db.writers.config_writer import get_ai_config
from app.db.writers.sprint_writer import create_sprint_summary, get_sprint_summaries
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.sprint import SprintSummaryData, SprintSummaryRequest

router = APIRouter(prefix="/sprints", tags=["Sprints"])


@router.post(
    "/{sprint_id}/summaries",
    response_model=ApiResponse[SprintSummaryData],
    status_code=status.HTTP_201_CREATED,
)
async def generate_sprint_summary(
    sprint_id: int,
    payload: SprintSummaryRequest,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[SprintSummaryData]:
    """Read sprint metadata + tasks, run LLM summary, and store in ai_sprint_summaries."""
    sprint_data = await get_sprint_full_context(session, sprint_id)
    if not sprint_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "sprint_not_found",
                    "message": f"Sprint with ID {sprint_id} was not found",
                },
            },
        )

    conf = await get_ai_config(session)
    selected_model = payload.model or conf.get("default_model", "llama3-8b")

    prompt = render_prompt(
        "summarise_sprint.j2",
        project_name=sprint_data.get("project_name", "Project"),
        name=sprint_data.get("name", ""),
        goal=sprint_data.get("goal"),
        status=sprint_data.get("status", "planning"),
        total_points=sprint_data.get("total_points", 0),
        completed_points=sprint_data.get("completed_points", 0),
        tasks=sprint_data.get("tasks", []),
    )

    inference_result = await engine_manager.generate_response(
        prompt=prompt,
        model_key=selected_model,
        max_tokens=payload.max_tokens,
        temperature=payload.temperature,
    )

    parsed = engine_manager.extract_json(inference_result["raw_text"])

    summary_text = str(parsed.get("summary_text", "No summary generated"))
    health_score = int(parsed.get("health_score", 75))
    risk_flags = parsed.get("risk_flags", [])
    if isinstance(risk_flags, str):
        risk_flags = [risk_flags]
    elif not isinstance(risk_flags, list):
        risk_flags = []

    summary_id = await create_sprint_summary(
        session=session,
        sprint_id=sprint_id,
        summary_text=summary_text,
        health_score=health_score,
        risk_flags=risk_flags,
        model_used=inference_result["model_used"],
    )

    return ApiResponse(
        success=True,
        data=SprintSummaryData(
            id=summary_id,
            sprint_id=sprint_id,
            summary_text=summary_text,
            health_score=health_score,
            risk_flags=risk_flags,
        ),
        meta=ResponseMeta(
            model_used=inference_result["model_used"],
            tokens_used=inference_result["tokens_used"],
            duration_ms=inference_result["duration_ms"],
        ),
    )


@router.get("/{sprint_id}/summaries", response_model=ApiResponse[list[dict[str, Any]]])
async def list_sprint_summaries(
    sprint_id: int,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[dict[str, Any]]]:
    """Retrieve history of AI summaries generated for a sprint."""
    summaries = await get_sprint_summaries(session, sprint_id)
    return ApiResponse(success=True, data=summaries)
