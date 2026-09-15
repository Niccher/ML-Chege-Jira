"""Background tasks REST endpoints for asynchronous long-running jobs."""

from typing import Any

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel

from app.core.llm_engine import engine_manager
from app.core.task_manager import task_manager
from app.core.security import verify_api_key
from fastapi import Depends

router = APIRouter(prefix="/async-tasks", tags=["Async Tasks"], dependencies=[Depends(verify_api_key)])

class GenerateRequest(BaseModel):
    prompt: str
    model: str | None = None
    max_tokens: int = 1024
    temperature: float = 0.2
    system_prompt: str | None = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

def _run_background_inference(task_id: str, payload: GenerateRequest):
    import asyncio
    
    async def _async_runner():
        task_manager.update_task(task_id, "running")
        try:
            inference_result = await engine_manager.generate_response(
                prompt=payload.prompt,
                model_key=payload.model,
                max_tokens=payload.max_tokens,
                temperature=payload.temperature,
                system_prompt=payload.system_prompt
            )
            # Try to parse as JSON if possible, else just string
            try:
                parsed = engine_manager.extract_json(inference_result["raw_text"])
                result_data = parsed
            except Exception:
                result_data = {"raw_text": inference_result["raw_text"]}
                
            task_manager.update_task(task_id, "completed", result=result_data)
        except Exception as e:
            task_manager.update_task(task_id, "failed", error=str(e))
            
    # Run the async runner in a new event loop if needed, or use the existing one
    # FastAPI background tasks run in threadpool, so we need to run asyncio event loop
    asyncio.run(_async_runner())


@router.post("/generate", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_generation_task(payload: GenerateRequest, background_tasks: BackgroundTasks):
    task_id = task_manager.create_task(payload.model)
    background_tasks.add_task(_run_background_inference, task_id, payload)
    return TaskResponse(
        task_id=task_id, 
        status="pending", 
        message="Task has been queued for background processing."
    )

@router.get("/{task_id}")
async def get_task_status(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error": {"code": "not_found", "message": "Task not found"}}
        )
    return {"success": True, "data": task}
