"""Q&A REST resource endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.llm_engine import engine_manager
from app.core.prompt_builder import render_prompt
from app.db.writers.config_writer import get_ai_config
from app.db.writers.qa_writer import create_qa_log
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.qa import QaData, QaRequest

router = APIRouter(prefix="/qa", tags=["Q&A"])


@router.post("", response_model=ApiResponse[QaData])
async def ask_question(
    payload: QaRequest,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[QaData]:
    """Execute grounded project question and answer."""
    conf = await get_ai_config(session)
    selected_model = payload.model or conf.get("default_model", "llama3-8b")

    prompt = render_prompt(
        "ask.j2",
        question=payload.question,
        context=payload.context,
    )

    inference_result = await engine_manager.generate_response(
        prompt=prompt,
        model_key=selected_model,
        max_tokens=1024,
        temperature=0.2,
    )

    parsed = engine_manager.extract_json(inference_result["raw_text"])
    answer = str(parsed.get("answer", inference_result["raw_text"]))

    qa_id = await create_qa_log(
        session=session,
        question=payload.question,
        context_json=payload.context,
        answer=answer,
        model_used=inference_result["model_used"],
    )

    return ApiResponse(
        success=True,
        data=QaData(
            id=qa_id,
            question=payload.question,
            answer=answer,
        ),
        meta=ResponseMeta(
            model_used=inference_result["model_used"],
            tokens_used=inference_result["tokens_used"],
            duration_ms=inference_result["duration_ms"],
        ),
    )
