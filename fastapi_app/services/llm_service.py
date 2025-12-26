# fastapi_app/services/llm_service.py
import logging
import requests
import json
from typing import Optional, List, Dict, Any
from fastapi_app.core.config import (
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY
)

logger = logging.getLogger(__name__)

# Default timeout in seconds
DEFAULT_TIMEOUT = 60


class LLMServiceError(Exception):
    """Custom exception for LLM service errors."""
    pass


def run_ollama(
    prompt: str,
    model: Optional[str] = None,
    timeout: Optional[int] = None,
    json_format: bool = False
) -> str:
    """
    Run inference using Ollama API.

    Args:
        prompt: The prompt to send
        model: Model to use (defaults to configured model)
        timeout: Request timeout in seconds (defaults to 60)
        json_format: If True, request JSON output from the model

    Returns:
        The model response text

    Raises:
        LLMServiceError: If the request fails
    """
    model = model or OLLAMA_MODEL
    timeout = timeout or DEFAULT_TIMEOUT
    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    # Request JSON format if specified
    if json_format:
        payload["format"] = "json"

    try:
        logger.info(f"Running Ollama inference: model={model}, timeout={timeout}s, json={json_format}")
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")

    except requests.exceptions.ConnectionError:
        raise LLMServiceError(
            f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
            "Ensure Ollama is running with 'ollama serve' or 'brew services start ollama'"
        )
    except requests.exceptions.Timeout:
        raise LLMServiceError(f"Ollama request timed out after {timeout} seconds")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise LLMServiceError(f"Model '{model}' not found. Use /models to see available models.")
        raise LLMServiceError(f"Ollama HTTP error: {e}")
    except Exception as e:
        raise LLMServiceError(f"Ollama error: {str(e)}")


def run_openai(
    prompt: str,
    model: str = "gpt-4",
    timeout: Optional[int] = None,
    json_format: bool = False
) -> str:
    """
    Run inference using OpenAI API (fallback option).

    Args:
        prompt: The prompt to send
        model: Model to use (defaults to gpt-4)
        timeout: Request timeout in seconds
        json_format: If True, request JSON output

    Returns:
        The model response text

    Raises:
        LLMServiceError: If the request fails
    """
    try:
        import openai
        openai.api_key = OPENAI_API_KEY

        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5
        }

        if timeout:
            kwargs["timeout"] = timeout

        if json_format:
            kwargs["response_format"] = {"type": "json_object"}

        response = openai.ChatCompletion.create(**kwargs)
        return response.choices[0].message["content"]

    except ImportError:
        raise LLMServiceError("OpenAI package not installed. Run: pip install openai")
    except Exception as e:
        raise LLMServiceError(f"OpenAI error: {str(e)}")


def run_llm(
    prompt: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    timeout: Optional[int] = None,
    json_format: bool = False
) -> str:
    """
    Run LLM inference using configured provider.

    Args:
        prompt: The prompt to send to the LLM
        provider: Override the default provider ('ollama' or 'openai')
        model: Override the default model
        timeout: Request timeout in seconds
        json_format: If True, request JSON output

    Returns:
        The LLM response text

    Raises:
        LLMServiceError: If the LLM service fails
    """
    provider = provider or LLM_PROVIDER
    logger.info(f"Running LLM inference with provider: {provider}")

    if provider == "ollama":
        return run_ollama(prompt, model=model, timeout=timeout, json_format=json_format)
    elif provider == "openai":
        if not OPENAI_API_KEY:
            raise LLMServiceError("OPENAI_API_KEY not set in environment")
        return run_openai(prompt, model=model or "gpt-4", timeout=timeout, json_format=json_format)
    else:
        raise LLMServiceError(f"Unknown LLM provider: {provider}")


def list_ollama_models() -> List[Dict[str, Any]]:
    """
    List available models from Ollama.

    Returns:
        List of model information dicts

    Raises:
        LLMServiceError: If the request fails
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("models", [])
    except requests.exceptions.ConnectionError:
        raise LLMServiceError(f"Cannot connect to Ollama at {OLLAMA_BASE_URL}")
    except Exception as e:
        raise LLMServiceError(f"Failed to list models: {str(e)}")


def check_model_exists(model: str) -> bool:
    """
    Check if a model exists in Ollama.

    Args:
        model: Model name to check

    Returns:
        True if model exists, False otherwise
    """
    try:
        models = list_ollama_models()
        model_names = [m.get("name", "") for m in models]
        return model in model_names
    except Exception:
        return False


def check_ollama_health() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def parse_json_response(response: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to parse a JSON response from the LLM.

    Args:
        response: The raw LLM response text

    Returns:
        Parsed JSON dict, or None if parsing fails
    """
    try:
        # Try direct JSON parse
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code blocks
    try:
        if "```json" in response:
            start = response.index("```json") + 7
            end = response.index("```", start)
            return json.loads(response[start:end].strip())
        elif "```" in response:
            start = response.index("```") + 3
            end = response.index("```", start)
            return json.loads(response[start:end].strip())
    except (json.JSONDecodeError, ValueError):
        pass

    return None
