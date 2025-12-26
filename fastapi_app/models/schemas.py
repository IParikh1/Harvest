# fastapi_app/models/schemas.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Any, Dict
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


class HarvestRequest(BaseModel):
    """Request model for harvest endpoint."""
    source: str = Field(..., min_length=1, description="Data source to analyze")
    query: str = Field(..., min_length=1, description="Query/question about the data")
    model: Optional[str] = Field(None, description="Model to use (e.g., 'llama3.2:1b', 'mistral:7b'). Defaults to configured model.")
    timeout: Optional[int] = Field(None, ge=10, le=300, description="Request timeout in seconds (10-300). Defaults to 60.")
    output_format: Optional[OutputFormat] = Field(OutputFormat.TEXT, description="Output format: 'text' or 'json'")
    callback_url: Optional[str] = Field(None, description="Webhook URL to POST results when complete")

    model_config = {
        "json_schema_extra": {
            "example": {
                "source": "Q4 2024 Revenue: $10M, Q3 2024: $8M, Q2 2024: $7M",
                "query": "What is the revenue growth trend?",
                "model": "llama3.2:1b",
                "timeout": 60,
                "output_format": "text"
            }
        }
    }


class BatchHarvestRequest(BaseModel):
    """Request model for batch harvest endpoint."""
    requests: List[HarvestRequest] = Field(..., min_length=1, max_length=10, description="List of harvest requests (max 10)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "requests": [
                    {"source": "Revenue: $10M", "query": "Summarize"},
                    {"source": "Costs: $5M", "query": "Analyze costs"}
                ]
            }
        }
    }


class BatchHarvestResponse(BaseModel):
    """Response model for batch harvest endpoint."""
    task_ids: List[str] = Field(..., description="List of task IDs for each request")
    count: int = Field(..., description="Number of tasks created")
    message: str = Field(..., description="Status message")


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
    model: Optional[str] = None
    result: Optional[str] = None
    result_json: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None


class ModelInfo(BaseModel):
    """Information about an available model."""
    name: str = Field(..., description="Model name (e.g., 'llama3.2:1b')")
    size: Optional[str] = Field(None, description="Model size")
    modified_at: Optional[str] = Field(None, description="Last modified timestamp")
    digest: Optional[str] = Field(None, description="Model digest/hash")


class ModelsResponse(BaseModel):
    """Response model for /models endpoint."""
    models: List[ModelInfo] = Field(..., description="List of available models")
    default_model: str = Field(..., description="Default model configured")
    count: int = Field(..., description="Number of available models")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    ollama_available: bool
    redis_available: bool
