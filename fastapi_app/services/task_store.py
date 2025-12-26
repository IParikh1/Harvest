# fastapi_app/services/task_store.py
"""
Task store with Redis persistence.
Falls back to in-memory storage if Redis is unavailable.
"""
import uuid
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi_app.models.schemas import TaskStatus
from fastapi_app.core.config import REDIS_URL, TASK_TTL_SECONDS

logger = logging.getLogger(__name__)

# Redis client (initialized lazily)
_redis_client = None
_use_redis = True

# Fallback in-memory store
_memory_store: Dict[str, Dict[str, Any]] = {}


def _get_redis():
    """Get or create Redis client."""
    global _redis_client, _use_redis

    if not _use_redis:
        return None

    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            _redis_client.ping()
            logger.info(f"Connected to Redis at {REDIS_URL}")
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory storage: {e}")
            _use_redis = False
            return None

    return _redis_client


def _task_key(task_id: str) -> str:
    """Generate Redis key for a task."""
    return f"harvest:task:{task_id}"


def _serialize_task(task: Dict[str, Any]) -> str:
    """Serialize task for Redis storage."""
    task_copy = task.copy()
    # Convert datetime to ISO format
    if task_copy.get("created_at"):
        task_copy["created_at"] = task_copy["created_at"].isoformat()
    if task_copy.get("completed_at"):
        task_copy["completed_at"] = task_copy["completed_at"].isoformat()
    # Convert enum to string
    if task_copy.get("status"):
        task_copy["status"] = task_copy["status"].value if hasattr(task_copy["status"], "value") else task_copy["status"]
    return json.dumps(task_copy)


def _deserialize_task(data: str) -> Dict[str, Any]:
    """Deserialize task from Redis storage."""
    task = json.loads(data)
    # Convert ISO format back to datetime
    if task.get("created_at"):
        task["created_at"] = datetime.fromisoformat(task["created_at"])
    if task.get("completed_at"):
        task["completed_at"] = datetime.fromisoformat(task["completed_at"])
    # Convert string back to enum
    if task.get("status"):
        task["status"] = TaskStatus(task["status"])
    return task


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
    task_data = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "source": source,
        "query": query,
        "result": None,
        "error": None,
        "created_at": datetime.utcnow(),
        "completed_at": None
    }

    redis_client = _get_redis()
    if redis_client:
        try:
            redis_client.setex(
                _task_key(task_id),
                TASK_TTL_SECONDS,
                _serialize_task(task_data)
            )
            # Add to sorted set for listing (score = timestamp)
            redis_client.zadd(
                "harvest:tasks",
                {task_id: task_data["created_at"].timestamp()}
            )
            logger.info(f"Created task {task_id} in Redis")
        except Exception as e:
            logger.error(f"Redis error creating task: {e}")
            _memory_store[task_id] = task_data
    else:
        _memory_store[task_id] = task_data
        logger.info(f"Created task {task_id} in memory")

    return task_id


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a task by ID.

    Args:
        task_id: The task identifier

    Returns:
        Task data dict or None if not found
    """
    redis_client = _get_redis()
    if redis_client:
        try:
            data = redis_client.get(_task_key(task_id))
            if data:
                return _deserialize_task(data)
            return None
        except Exception as e:
            logger.error(f"Redis error getting task: {e}")
            return _memory_store.get(task_id)

    return _memory_store.get(task_id)


def _update_task(task_id: str, updates: Dict[str, Any]) -> bool:
    """
    Internal function to update a task.

    Args:
        task_id: The task identifier
        updates: Dictionary of fields to update

    Returns:
        True if updated, False if task not found
    """
    redis_client = _get_redis()
    if redis_client:
        try:
            data = redis_client.get(_task_key(task_id))
            if not data:
                return False

            task = _deserialize_task(data)
            task.update(updates)

            # Get remaining TTL or use default
            ttl = redis_client.ttl(_task_key(task_id))
            if ttl < 0:
                ttl = TASK_TTL_SECONDS

            redis_client.setex(
                _task_key(task_id),
                ttl,
                _serialize_task(task)
            )
            return True
        except Exception as e:
            logger.error(f"Redis error updating task: {e}")
            if task_id in _memory_store:
                _memory_store[task_id].update(updates)
                return True
            return False

    if task_id not in _memory_store:
        return False
    _memory_store[task_id].update(updates)
    return True


def update_task_status(task_id: str, status: TaskStatus) -> bool:
    """
    Update the status of a task.

    Args:
        task_id: The task identifier
        status: New status

    Returns:
        True if updated, False if task not found
    """
    result = _update_task(task_id, {"status": status})
    if result:
        logger.info(f"Task {task_id} status updated to {status}")
    return result


def complete_task(task_id: str, result: str) -> bool:
    """
    Mark a task as completed with result.

    Args:
        task_id: The task identifier
        result: The LLM result

    Returns:
        True if updated, False if task not found
    """
    success = _update_task(task_id, {
        "status": TaskStatus.COMPLETED,
        "result": result,
        "completed_at": datetime.utcnow()
    })
    if success:
        logger.info(f"Task {task_id} completed")
    return success


def fail_task(task_id: str, error: str) -> bool:
    """
    Mark a task as failed with error message.

    Args:
        task_id: The task identifier
        error: Error message

    Returns:
        True if updated, False if task not found
    """
    success = _update_task(task_id, {
        "status": TaskStatus.FAILED,
        "error": error,
        "completed_at": datetime.utcnow()
    })
    if success:
        logger.error(f"Task {task_id} failed: {error}")
    return success


def list_tasks(limit: int = 100) -> List[Dict[str, Any]]:
    """
    List recent tasks.

    Args:
        limit: Maximum number of tasks to return

    Returns:
        List of task dicts, sorted by creation time (newest first)
    """
    redis_client = _get_redis()
    if redis_client:
        try:
            # Get task IDs from sorted set (newest first)
            task_ids = redis_client.zrevrange("harvest:tasks", 0, limit - 1)
            tasks = []
            for task_id in task_ids:
                task = get_task(task_id)
                if task:
                    tasks.append(task)
            return tasks
        except Exception as e:
            logger.error(f"Redis error listing tasks: {e}")
            # Fall through to memory store

    tasks = list(_memory_store.values())
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    return tasks[:limit]


def clear_tasks() -> None:
    """
    Clear all tasks. Used for testing.
    """
    global _memory_store
    redis_client = _get_redis()
    if redis_client:
        try:
            # Get all task keys and delete them
            keys = redis_client.keys("harvest:task:*")
            if keys:
                redis_client.delete(*keys)
            redis_client.delete("harvest:tasks")
            logger.info("Cleared all tasks from Redis")
        except Exception as e:
            logger.error(f"Redis error clearing tasks: {e}")

    _memory_store = {}
    logger.info("Cleared in-memory task store")
