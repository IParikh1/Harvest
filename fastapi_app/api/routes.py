# fastapi_app/api/routes.py
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi_app.models.schemas import (
    HarvestRequest,
    HarvestResponse,
    TaskResult,
    TaskStatus,
    HealthResponse
)
from fastapi_app.services.task_store import (
    create_task,
    get_task,
    update_task_status,
    complete_task,
    fail_task,
    list_tasks
)
from fastapi_app.services.llm_service import run_llm, check_ollama_health, LLMServiceError
from fastapi_app.core.config import API_VERSION

logger = logging.getLogger(__name__)
router = APIRouter()


def process_harvest_task(task_id: str, source: str, query: str):
    """
    Background task to process harvest request.

    Args:
        task_id: The task identifier
        source: Data source to analyze
        query: Query about the data
    """
    try:
        update_task_status(task_id, TaskStatus.PROCESSING)

        # Build prompt
        prompt = f"""Analyze the following data and answer the query.

Data:
{source}

Query: {query}

Provide a clear, concise analysis based on the data provided."""

        # Run LLM inference
        result = run_llm(prompt)
        complete_task(task_id, result)

    except LLMServiceError as e:
        logger.error(f"LLM error for task {task_id}: {e}")
        fail_task(task_id, str(e))
    except Exception as e:
        logger.error(f"Unexpected error for task {task_id}: {e}")
        fail_task(task_id, f"Internal error: {str(e)}")


@router.post("/harvest", response_model=HarvestResponse, tags=["Harvest"])
async def run_harvest(request: HarvestRequest, background_tasks: BackgroundTasks):
    """
    Submit a harvest request for analysis.

    The request is processed asynchronously. Use the returned task_id
    to check the status and retrieve results.
    """
    logger.info(f"Received harvest request: query='{request.query[:50]}...'")

    # Create task
    task_id = create_task(request.source, request.query)

    # Queue background processing
    background_tasks.add_task(
        process_harvest_task,
        task_id,
        request.source,
        request.query
    )

    return HarvestResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="Harvest task queued successfully"
    )


@router.get("/harvest/{task_id}", response_model=TaskResult, tags=["Harvest"])
async def get_harvest_result(task_id: str):
    """
    Retrieve the result of a harvest task.

    Args:
        task_id: The task identifier returned from POST /harvest
    """
    task = get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return TaskResult(**task)


@router.get("/tasks", tags=["Tasks"])
async def list_all_tasks(limit: int = 20):
    """
    List recent harvest tasks.

    Args:
        limit: Maximum number of tasks to return (default 20)
    """
    tasks = list_tasks(limit=limit)
    return {"tasks": tasks, "count": len(tasks)}


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Check the health of the API and its dependencies.
    """
    ollama_ok = check_ollama_health()

    # For MVP, we're using in-memory store, so Redis check is placeholder
    redis_ok = True  # Would check actual Redis in production

    status = "healthy" if ollama_ok else "degraded"

    return HealthResponse(
        status=status,
        version=API_VERSION,
        ollama_available=ollama_ok,
        redis_available=redis_ok
    )
