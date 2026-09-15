"""Project wiki generation REST endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.llm_engine import engine_manager
from app.core.prompt_builder import render_prompt
from app.db.readers.project_reader import get_project_with_tasks_and_wiki
from app.db.writers.config_writer import get_ai_config
from app.db.writers.wiki_writer import create_wiki_page
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.project import WikiGenerateData, WikiGenerateRequest

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "/{project_id}/wiki-pages",
    response_model=ApiResponse[WikiGenerateData],
    status_code=status.HTTP_201_CREATED,
)
async def generate_project_wiki_page(
    project_id: int,
    payload: WikiGenerateRequest,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[WikiGenerateData]:
    """Auto-generate a rich markdown wiki page grounded in project tasks and tech stack."""
    project_data = await get_project_with_tasks_and_wiki(session, project_id)
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "project_not_found",
                    "message": f"Project with ID {project_id} was not found",
                },
            },
        )

    conf = await get_ai_config(session)
    selected_model = payload.model or conf.get("default_model", "llama3-8b")

    prompt = render_prompt(
        "generate_wiki.j2",
        name=project_data.get("name", "Project"),
        description=project_data.get("description", ""),
        tech_stack=project_data.get("tech_stack"),
        repository_url=project_data.get("repository_url"),
        page_title=payload.page_title,
        custom_instructions=payload.custom_instructions,
        tasks=project_data.get("tasks", []),
    )

    inference_result = await engine_manager.generate_response(
        prompt=prompt,
        model_key=selected_model,
        max_tokens=2048,
        temperature=0.3,
    )

    parsed = engine_manager.extract_json(inference_result["raw_text"])
    content = str(parsed.get("content", f"# {payload.page_title}\n\nGenerated documentation."))

    # Insert into project_wiki_pages
    created_page = await create_wiki_page(
        session=session,
        project_id=project_id,
        title=payload.page_title,
        content=content,
        parent_id=payload.parent_id,
        created_by=payload.created_by,
    )

    return ApiResponse(
        success=True,
        data=WikiGenerateData(
            id=created_page["id"],
            project_id=project_id,
            parent_id=created_page["parent_id"],
            title=created_page["title"],
            slug=created_page["slug"],
            content=created_page["content"],
            version=created_page["version"],
        ),
        meta=ResponseMeta(
            model_used=inference_result["model_used"],
            tokens_used=inference_result["tokens_used"],
            duration_ms=inference_result["duration_ms"],
        ),
    )
