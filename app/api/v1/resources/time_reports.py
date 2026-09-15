"""Time report REST resource endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.llm_engine import engine_manager
from app.core.prompt_builder import render_prompt
from app.db.readers.timelog_reader import get_user_time_logs
from app.db.writers.config_writer import get_ai_config
from app.db.writers.timelog_writer import create_time_report
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.time_report import TimeReportData, TimeReportRequest

router = APIRouter(prefix="/time-reports", tags=["Time Reports"])


@router.post("", response_model=ApiResponse[TimeReportData], status_code=status.HTTP_201_CREATED)
async def generate_time_report(
    payload: TimeReportRequest,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[TimeReportData]:
    """Analyze developer time logs over a date range and store narrative report."""
    logs = await get_user_time_logs(
        session=session,
        user_id=payload.user_id,
        project_id=payload.project_id,
        from_date=payload.period_from,
        to_date=payload.period_to,
    )

    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "no_logs_found",
                    "message": "No time logs found matching the given criteria",
                },
            },
        )

    conf = await get_ai_config(session)
    selected_model = payload.model or conf.get("default_model", "phi3-mini")

    prompt = render_prompt(
        "analyse_timelogs.j2",
        period_from=payload.period_from,
        period_to=payload.period_to,
        logs=logs,
    )

    inference_result = await engine_manager.generate_response(
        prompt=prompt,
        model_key=selected_model,
        max_tokens=1500,
        temperature=0.2,
    )

    parsed = engine_manager.extract_json(inference_result["raw_text"])
    report_text = str(parsed.get("report_text", "Time log report generated."))

    report_id = await create_time_report(
        session=session,
        user_id=payload.user_id,
        project_id=payload.project_id,
        period_from=payload.period_from,
        period_to=payload.period_to,
        report_text=report_text,
        model_used=inference_result["model_used"],
    )

    return ApiResponse(
        success=True,
        data=TimeReportData(
            id=report_id,
            user_id=payload.user_id,
            project_id=payload.project_id,
            period_from=payload.period_from,
            period_to=payload.period_to,
            report_text=report_text,
        ),
        meta=ResponseMeta(
            model_used=inference_result["model_used"],
            tokens_used=inference_result["tokens_used"],
            duration_ms=inference_result["duration_ms"],
        ),
    )
