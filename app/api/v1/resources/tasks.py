"""Task enhancements and priority suggestion REST endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.llm_engine import engine_manager
from app.core.prompt_builder import render_prompt
from app.db.readers.task_reader import get_task_with_project
from app.db.writers.config_writer import get_ai_config
from app.db.writers.task_writer import create_task_enhancement, get_task_enhancements
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.task import (
    PrioritySuggestData,
    PrioritySuggestRequest,
    TaskEnhanceData,
    TaskEnhanceRequest,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/{task_id}/enhancements",
    response_model=ApiResponse[TaskEnhanceData],
    status_code=status.HTTP_201_CREATED,
)
async def enhance_task(
    task_id: int,
    payload: TaskEnhanceRequest,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[TaskEnhanceData]:
    """Read task from DB, expand into detailed ticket via LLM, and store in ai_task_enhancements."""
    task = await get_task_with_project(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "task_not_found",
                    "message": f"Task with ID {task_id} was not found",
                },
            },
        )

    conf = await get_ai_config(session)
    selected_model = payload.model or conf.get("default_model", "mistral-7b")

    # Render prompt
    prompt = render_prompt(
        "enhance_task.j2",
        project_name=task.get("project_name") or "General Project",
        project_tech_stack=task.get("project_tech_stack"),
        title=task.get("title", ""),
        description=task.get("description", ""),
        status=task.get("status", "todo"),
    )

    # Run inference
    inference_result = await engine_manager.generate_response(
        prompt=prompt,
        model_key=selected_model,
        max_tokens=payload.max_tokens,
        temperature=payload.temperature,
    )

    # Extract JSON
    parsed = engine_manager.extract_json(inference_result["raw_text"])

    summary = str(parsed.get("summary", task.get("title", "")))
    criteria = parsed.get("acceptance_criteria", [])
    if isinstance(criteria, str):
        criteria = [criteria]
    elif not isinstance(criteria, list):
        criteria = []

    story_points = parsed.get("story_points")
    if story_points is not None:
        try:
            story_points = int(story_points)
        except (ValueError, TypeError):
            story_points = None

    priority = parsed.get("priority", "medium")
    if priority not in ["low", "medium", "high", "critical"]:
        priority = "medium"

    # Write to DB
    enhancement_id = await create_task_enhancement(
        session=session,
        task_id=task_id,
        summary=summary,
        acceptance_criteria=criteria,
        story_points=story_points,
        priority=priority,
        model_used=inference_result["model_used"],
        tokens_used=inference_result["tokens_used"],
    )

    return ApiResponse(
        success=True,
        data=TaskEnhanceData(
            id=enhancement_id,
            task_id=task_id,
            summary=summary,
            acceptance_criteria=criteria,
            story_points=story_points,
            priority=priority,  # type: ignore[arg-type]
        ),
        meta=ResponseMeta(
            model_used=inference_result["model_used"],
            tokens_used=inference_result["tokens_used"],
            duration_ms=inference_result["duration_ms"],
        ),
    )


@router.get("/{task_id}/enhancements", response_model=ApiResponse[list[dict[str, Any]]])
async def list_task_enhancements(
    task_id: int,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[dict[str, Any]]]:
    """Retrieve history of AI enhancements generated for a task."""
    enhancements = await get_task_enhancements(session, task_id)
    return ApiResponse(success=True, data=enhancements)


@router.post(
    "/{task_id}/priority-suggestions",
    response_model=ApiResponse[PrioritySuggestData],
    status_code=status.HTTP_201_CREATED,
)
async def suggest_task_priority(
    task_id: int,
    payload: PrioritySuggestRequest,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[PrioritySuggestData]:
    """Suggest priority and story points for a task."""
    task = await get_task_with_project(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "task_not_found",
                    "message": f"Task with ID {task_id} was not found",
                },
            },
        )

    conf = await get_ai_config(session)
    selected_model = payload.model or conf.get("default_model", "phi3-mini")

    prompt = render_prompt(
        "suggest_priority.j2",
        project_name=task.get("project_name") or "General Project",
        title=task.get("title", ""),
        description=task.get("description", ""),
    )

    inference_result = await engine_manager.generate_response(
        prompt=prompt,
        model_key=selected_model,
        max_tokens=256,
        temperature=0.1,
    )

    parsed = engine_manager.extract_json(inference_result["raw_text"])

    priority = parsed.get("priority", "medium")
    if priority not in ["low", "medium", "high", "critical"]:
        priority = "medium"

    story_points = int(parsed.get("story_points", 3))
    reasoning = parsed.get("reasoning")

    # Persist in ai_task_enhancements
    await create_task_enhancement(
        session=session,
        task_id=task_id,
        summary=reasoning or f"Suggested priority: {priority}, points: {story_points}",
        acceptance_criteria=[],
        story_points=story_points,
        priority=priority,
        model_used=inference_result["model_used"],
        tokens_used=inference_result["tokens_used"],
    )

    return ApiResponse(
        success=True,
        data=PrioritySuggestData(
            task_id=task_id,
            priority=priority,  # type: ignore[arg-type]
            story_points=story_points,
            reasoning=reasoning,
        ),
        meta=ResponseMeta(
            model_used=inference_result["model_used"],
            tokens_used=inference_result["tokens_used"],
            duration_ms=inference_result["duration_ms"],
        ),
    )
