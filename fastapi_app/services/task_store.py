# fastapi_app/services/task_store.py
"""
Simple in-memory task store for MVP.
For production, replace with Redis or database storage.
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi_app.models.schemas import TaskStatus

logger = logging.getLogger(__name__)

# In-memory store (replace with Redis for production)
_task_store: Dict[str, Dict[str, Any]] = {}


def create_task(source: str, query: str) -> str:
    """
    Create a new task and return its ID.

    Args:
        source: The data source
        query: The query to analyze

    Returns:
        task_id: Unique identifier for the task
    """
    task_id = str(uuid.uuid4())
    _task_store[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "source": source,
        "query": query,
        "result": None,
        "error": None,
        "created_at": datetime.utcnow(),
        "completed_at": None
    }
    logger.info(f"Created task {task_id}")
    return task_id


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a task by ID.

    Args:
        task_id: The task identifier

    Returns:
        Task data dict or None if not found
    """
    return _task_store.get(task_id)


def update_task_status(task_id: str, status: TaskStatus) -> bool:
    """
    Update the status of a task.

    Args:
        task_id: The task identifier
        status: New status

    Returns:
        True if updated, False if task not found
    """
    if task_id not in _task_store:
        return False
    _task_store[task_id]["status"] = status
    logger.info(f"Task {task_id} status updated to {status}")
    return True


def complete_task(task_id: str, result: str) -> bool:
    """
    Mark a task as completed with result.

    Args:
        task_id: The task identifier
        result: The LLM result

    Returns:
        True if updated, False if task not found
    """
    if task_id not in _task_store:
        return False
    _task_store[task_id]["status"] = TaskStatus.COMPLETED
    _task_store[task_id]["result"] = result
    _task_store[task_id]["completed_at"] = datetime.utcnow()
    logger.info(f"Task {task_id} completed")
    return True


def fail_task(task_id: str, error: str) -> bool:
    """
    Mark a task as failed with error message.

    Args:
        task_id: The task identifier
        error: Error message

    Returns:
        True if updated, False if task not found
    """
    if task_id not in _task_store:
        return False
    _task_store[task_id]["status"] = TaskStatus.FAILED
    _task_store[task_id]["error"] = error
    _task_store[task_id]["completed_at"] = datetime.utcnow()
    logger.error(f"Task {task_id} failed: {error}")
    return True


def list_tasks(limit: int = 100) -> list:
    """
    List recent tasks.

    Args:
        limit: Maximum number of tasks to return

    Returns:
        List of task dicts
    """
    tasks = list(_task_store.values())
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    return tasks[:limit]
