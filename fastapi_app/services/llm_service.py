# fastapi_app/services/llm_service.py
import logging
import requests
from typing import Optional
from fastapi_app.core.config import (
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY
)

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Custom exception for LLM service errors."""
    pass


def run_ollama(prompt: str, model: Optional[str] = None) -> str:
    """Run inference using Ollama API."""
    model = model or OLLAMA_MODEL
    url = f"{OLLAMA_BASE_URL}/api/generate"

    try:
        response = requests.post(
            url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except requests.exceptions.ConnectionError:
        raise LLMServiceError(
            f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
            "Ensure Ollama is running with 'ollama serve' or 'brew services start ollama'"
        )
    except requests.exceptions.Timeout:
        raise LLMServiceError("Ollama request timed out after 120 seconds")
    except requests.exceptions.HTTPError as e:
        raise LLMServiceError(f"Ollama HTTP error: {e}")
    except Exception as e:
        raise LLMServiceError(f"Ollama error: {str(e)}")


def run_openai(prompt: str, model: str = "gpt-4") -> str:
    """Run inference using OpenAI API (fallback option)."""
    try:
        import openai
        openai.api_key = OPENAI_API_KEY

        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message["content"]
    except ImportError:
        raise LLMServiceError("OpenAI package not installed. Run: pip install openai")
    except Exception as e:
        raise LLMServiceError(f"OpenAI error: {str(e)}")


def run_llm(prompt: str, provider: Optional[str] = None) -> str:
    """
    Run LLM inference using configured provider.

    Args:
        prompt: The prompt to send to the LLM
        provider: Override the default provider ('ollama' or 'openai')

    Returns:
        The LLM response text

    Raises:
        LLMServiceError: If the LLM service fails
    """
    provider = provider or LLM_PROVIDER
    logger.info(f"Running LLM inference with provider: {provider}")

    if provider == "ollama":
        return run_ollama(prompt)
    elif provider == "openai":
        if not OPENAI_API_KEY:
            raise LLMServiceError("OPENAI_API_KEY not set in environment")
        return run_openai(prompt)
    else:
        raise LLMServiceError(f"Unknown LLM provider: {provider}")


def check_ollama_health() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False
