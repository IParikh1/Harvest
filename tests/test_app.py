# tests/test_app.py
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi_app.main import app
from fastapi_app.services.task_store import (
    create_task,
    get_task,
    complete_task,
    fail_task,
    update_task_status,
    clear_tasks,
    _memory_store
)
from fastapi_app.models.schemas import TaskStatus
from fastapi_app.services.llm_service import run_ollama, LLMServiceError, check_ollama_health

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check_returns_200(self):
        """Health endpoint should return 200."""
        with patch('fastapi_app.api.routes.check_ollama_health', return_value=True):
            with patch('fastapi_app.api.routes.check_redis_health', return_value=True):
                response = client.get("/health")
                assert response.status_code == 200

    def test_health_check_shows_ollama_status(self):
        """Health check should report Ollama availability."""
        with patch('fastapi_app.api.routes.check_ollama_health', return_value=True):
            with patch('fastapi_app.api.routes.check_redis_health', return_value=True):
                response = client.get("/health")
                data = response.json()
                assert "ollama_available" in data
                assert data["ollama_available"] is True

    def test_health_check_degraded_when_ollama_down(self):
        """Health should be degraded when Ollama is unavailable."""
        with patch('fastapi_app.api.routes.check_ollama_health', return_value=False):
            with patch('fastapi_app.api.routes.check_redis_health', return_value=True):
                response = client.get("/health")
                data = response.json()
                assert data["status"] == "unhealthy"
                assert data["ollama_available"] is False

    def test_health_check_shows_redis_status(self):
        """Health check should report Redis availability."""
        with patch('fastapi_app.api.routes.check_ollama_health', return_value=True):
            with patch('fastapi_app.api.routes.check_redis_health', return_value=False):
                response = client.get("/health")
                data = response.json()
                assert "redis_available" in data
                assert data["status"] == "degraded"


class TestHarvestEndpoint:
    """Tests for the /harvest endpoints."""

    def setup_method(self):
        """Clear task store before each test."""
        clear_tasks()

    def test_harvest_post_returns_task_id(self):
        """POST /harvest should return a task_id."""
        with patch('fastapi_app.api.routes.process_harvest_task'):
            response = client.post(
                "/harvest",
                json={"source": "test data", "query": "test query"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "pending"

    def test_harvest_post_validates_input(self):
        """POST /harvest should validate required fields."""
        response = client.post("/harvest", json={})
        assert response.status_code == 422  # Validation error

    def test_harvest_post_rejects_empty_source(self):
        """POST /harvest should reject empty source."""
        response = client.post(
            "/harvest",
            json={"source": "", "query": "test"}
        )
        assert response.status_code == 422

    def test_harvest_post_rejects_whitespace_source(self):
        """POST /harvest should reject whitespace-only source."""
        response = client.post(
            "/harvest",
            json={"source": "   ", "query": "test"}
        )
        assert response.status_code == 400
        assert "empty or whitespace" in response.json()["detail"]

    def test_harvest_get_returns_task(self):
        """GET /harvest/{task_id} should return task details."""
        # Create a task directly
        task_id = create_task("test source", "test query")
        complete_task(task_id, "test result")

        response = client.get(f"/harvest/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["status"] == "completed"
        assert data["result"] == "test result"

    def test_harvest_get_returns_404_for_unknown_task(self):
        """GET /harvest/{task_id} should return 404 for unknown task."""
        response = client.get("/harvest/unknown-task-id")
        assert response.status_code == 404


class TestInputValidation:
    """Tests for input validation and sanitization."""

    def setup_method(self):
        """Clear task store before each test."""
        clear_tasks()

    def test_rejects_oversized_source(self):
        """Should reject source exceeding max length."""
        oversized_source = "x" * 60000  # Exceeds 50KB default
        response = client.post(
            "/harvest",
            json={"source": oversized_source, "query": "test"}
        )
        assert response.status_code == 400
        assert "exceeds maximum length" in response.json()["detail"]

    def test_rejects_oversized_query(self):
        """Should reject query exceeding max length."""
        oversized_query = "x" * 2000  # Exceeds 1000 char default
        response = client.post(
            "/harvest",
            json={"source": "test data", "query": oversized_query}
        )
        assert response.status_code == 400
        assert "exceeds maximum length" in response.json()["detail"]


class TestTaskStore:
    """Tests for the task store service."""

    def setup_method(self):
        """Clear task store before each test."""
        clear_tasks()

    def test_create_task_returns_uuid(self):
        """create_task should return a UUID string."""
        task_id = create_task("source", "query")
        assert task_id is not None
        assert len(task_id) == 36  # UUID format

    def test_get_task_returns_task_data(self):
        """get_task should return task data."""
        task_id = create_task("source", "query")
        task = get_task(task_id)
        assert task is not None
        assert task["source"] == "source"
        assert task["query"] == "query"
        assert task["status"] == TaskStatus.PENDING

    def test_get_task_returns_none_for_unknown(self):
        """get_task should return None for unknown task."""
        task = get_task("unknown")
        assert task is None

    def test_complete_task_updates_status(self):
        """complete_task should update status and result."""
        task_id = create_task("source", "query")
        complete_task(task_id, "result")
        task = get_task(task_id)
        assert task["status"] == TaskStatus.COMPLETED
        assert task["result"] == "result"
        assert task["completed_at"] is not None

    def test_fail_task_updates_status(self):
        """fail_task should update status and error."""
        task_id = create_task("source", "query")
        fail_task(task_id, "error message")
        task = get_task(task_id)
        assert task["status"] == TaskStatus.FAILED
        assert task["error"] == "error message"

    def test_update_task_status(self):
        """update_task_status should change status."""
        task_id = create_task("source", "query")
        update_task_status(task_id, TaskStatus.PROCESSING)
        task = get_task(task_id)
        assert task["status"] == TaskStatus.PROCESSING


class TestLLMService:
    """Tests for the LLM service."""

    def test_run_ollama_success(self):
        """run_ollama should return response on success."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "test response"}
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response):
            result = run_ollama("test prompt")
            assert result == "test response"

    def test_run_ollama_connection_error(self):
        """run_ollama should raise LLMServiceError on connection failure."""
        with patch('requests.post', side_effect=Exception("Connection refused")):
            with pytest.raises(LLMServiceError):
                run_ollama("test prompt")

    def test_check_ollama_health_success(self):
        """check_ollama_health should return True when Ollama is running."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch('requests.get', return_value=mock_response):
            assert check_ollama_health() is True

    def test_check_ollama_health_failure(self):
        """check_ollama_health should return False when Ollama is down."""
        with patch('requests.get', side_effect=Exception("Connection refused")):
            assert check_ollama_health() is False


class TestTasksEndpoint:
    """Tests for the /tasks endpoint."""

    def setup_method(self):
        """Clear task store before each test."""
        clear_tasks()

    def test_list_tasks_empty(self):
        """GET /tasks should return empty list when no tasks."""
        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["count"] == 0

    def test_list_tasks_returns_tasks(self):
        """GET /tasks should return created tasks."""
        create_task("source1", "query1")
        create_task("source2", "query2")

        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["tasks"]) == 2


class TestAuthEndpoint:
    """Tests for authentication endpoints."""

    def test_auth_status_returns_disabled_by_default(self):
        """GET /auth/status should show auth disabled when no API_KEYS."""
        response = client.get("/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["auth_enabled"] is False

    def test_auth_status_with_api_keys(self):
        """GET /auth/status should show auth enabled when API_KEYS set."""
        with patch('fastapi_app.core.auth.API_KEYS', ['test-key']):
            with patch('fastapi_app.api.routes.is_auth_enabled', return_value=True):
                response = client.get("/auth/status")
                assert response.status_code == 200


class TestP1Features:
    """Tests for P1 features: model selection, timeout, JSON output, batch, webhooks."""

    def setup_method(self):
        """Clear task store before each test."""
        clear_tasks()

    def test_harvest_with_model_parameter(self):
        """POST /harvest should accept model parameter."""
        with patch('fastapi_app.api.routes.process_harvest_task'):
            response = client.post(
                "/harvest",
                json={
                    "source": "test data",
                    "query": "test query",
                    "model": "llama3.2:1b"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data

    def test_harvest_with_timeout_parameter(self):
        """POST /harvest should accept timeout parameter."""
        with patch('fastapi_app.api.routes.process_harvest_task'):
            response = client.post(
                "/harvest",
                json={
                    "source": "test data",
                    "query": "test query",
                    "timeout": 120
                }
            )
            assert response.status_code == 200

    def test_harvest_with_json_output_format(self):
        """POST /harvest should accept output_format parameter."""
        with patch('fastapi_app.api.routes.process_harvest_task'):
            response = client.post(
                "/harvest",
                json={
                    "source": "test data",
                    "query": "test query",
                    "output_format": "json"
                }
            )
            assert response.status_code == 200

    def test_harvest_with_callback_url(self):
        """POST /harvest should accept callback_url parameter."""
        with patch('fastapi_app.api.routes.process_harvest_task'):
            response = client.post(
                "/harvest",
                json={
                    "source": "test data",
                    "query": "test query",
                    "callback_url": "https://example.com/webhook"
                }
            )
            assert response.status_code == 200

    def test_batch_harvest_endpoint(self):
        """POST /harvest/batch should create multiple tasks."""
        with patch('fastapi_app.api.routes.process_harvest_task'):
            response = client.post(
                "/harvest/batch",
                json={
                    "requests": [
                        {"source": "data 1", "query": "query 1"},
                        {"source": "data 2", "query": "query 2"},
                        {"source": "data 3", "query": "query 3"}
                    ]
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 3
            assert len(data["task_ids"]) == 3

    def test_batch_harvest_validates_max_requests(self):
        """POST /harvest/batch should reject more than 10 requests."""
        requests_list = [{"source": f"data {i}", "query": f"query {i}"} for i in range(11)]
        response = client.post(
            "/harvest/batch",
            json={"requests": requests_list}
        )
        assert response.status_code == 422  # Validation error

    def test_models_endpoint(self):
        """GET /models should return list of models."""
        mock_models = [
            {"name": "llama3.2:1b", "size": 1300000000, "modified_at": "2024-01-01"},
            {"name": "mistral:7b", "size": 4100000000, "modified_at": "2024-01-02"}
        ]
        with patch('fastapi_app.api.routes.list_ollama_models', return_value=mock_models):
            response = client.get("/models")
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 2
            assert len(data["models"]) == 2
            assert "default_model" in data

    def test_models_endpoint_when_ollama_unavailable(self):
        """GET /models should return 503 when Ollama is unavailable."""
        from fastapi_app.services.llm_service import LLMServiceError
        with patch('fastapi_app.api.routes.list_ollama_models', side_effect=LLMServiceError("Cannot connect")):
            response = client.get("/models")
            assert response.status_code == 503

    def test_task_result_includes_new_fields(self):
        """Task result should include new P1 fields."""
        # Create task with new parameters
        task_id = create_task(
            source="test",
            query="test",
            model="llama3.2:1b",
            timeout=60,
            output_format="json"
        )

        response = client.get(f"/harvest/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["model"] == "llama3.2:1b"


class TestLLMServiceP1:
    """Tests for LLM service P1 features."""

    def test_run_ollama_with_timeout(self):
        """run_ollama should respect timeout parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "test response"}
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response) as mock_post:
            from fastapi_app.services.llm_service import run_ollama
            result = run_ollama("test prompt", timeout=30)
            assert result == "test response"
            # Verify timeout was passed
            mock_post.assert_called_once()
            assert mock_post.call_args[1]["timeout"] == 30

    def test_run_ollama_with_json_format(self):
        """run_ollama should request JSON format when specified."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": '{"key": "value"}'}
        mock_response.raise_for_status = MagicMock()

        with patch('requests.post', return_value=mock_response) as mock_post:
            from fastapi_app.services.llm_service import run_ollama
            result = run_ollama("test prompt", json_format=True)
            # Verify format was passed in payload
            call_json = mock_post.call_args[1]["json"]
            assert call_json.get("format") == "json"

    def test_parse_json_response_valid(self):
        """parse_json_response should parse valid JSON."""
        from fastapi_app.services.llm_service import parse_json_response
        result = parse_json_response('{"key": "value", "number": 42}')
        assert result == {"key": "value", "number": 42}

    def test_parse_json_response_code_block(self):
        """parse_json_response should extract JSON from code blocks."""
        from fastapi_app.services.llm_service import parse_json_response
        result = parse_json_response('Here is the result:\n```json\n{"key": "value"}\n```')
        assert result == {"key": "value"}

    def test_parse_json_response_invalid(self):
        """parse_json_response should return None for invalid JSON."""
        from fastapi_app.services.llm_service import parse_json_response
        result = parse_json_response('This is not JSON at all')
        assert result is None

    def test_list_ollama_models(self):
        """list_ollama_models should return model list."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "models": [{"name": "llama3.2:1b"}, {"name": "mistral:7b"}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('requests.get', return_value=mock_response):
            from fastapi_app.services.llm_service import list_ollama_models
            models = list_ollama_models()
            assert len(models) == 2
            assert models[0]["name"] == "llama3.2:1b"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
