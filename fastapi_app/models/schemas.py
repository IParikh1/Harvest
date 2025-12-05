# fastapi_app/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class HarvestRequest(BaseModel):
    """Request model for harvest endpoint."""
    source: str = Field(..., min_length=1, description="Data source to analyze")
    query: str = Field(..., min_length=1, description="Query/question about the data")

    model_config = {
        "json_schema_extra": {
            "example": {
                "source": "Q4 2024 Revenue: $10M, Q3 2024: $8M, Q2 2024: $7M",
                "query": "What is the revenue growth trend?"
            }
        }
    }


class HarvestResponse(BaseModel):
    """Response model for harvest endpoint."""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    message: str = Field(..., description="Status message")


class TaskResult(BaseModel):
    """Model for task result retrieval."""
    task_id: str
    status: TaskStatus
    source: Optional[str] = None
    query: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    ollama_available: bool
    redis_available: bool
