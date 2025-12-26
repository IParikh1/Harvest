# fastapi_app/core/auth.py
"""
API Key authentication for Harvest API.
"""
import logging
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from fastapi_app.core.config import API_KEYS

logger = logging.getLogger(__name__)

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def is_auth_enabled() -> bool:
    """Check if authentication is enabled (API_KEYS is configured)."""
    return len(API_KEYS) > 0


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Verify the API key from request header.

    If API_KEYS is not configured, authentication is disabled (development mode).
    If API_KEYS is configured, a valid key must be provided.

    Args:
        api_key: The API key from X-API-Key header

    Returns:
        The validated API key, or None if auth is disabled

    Raises:
        HTTPException: 401 if auth is enabled and key is missing/invalid
    """
    # If no API keys configured, auth is disabled
    if not is_auth_enabled():
        logger.debug("Authentication disabled (no API_KEYS configured)")
        return None

    # Auth is enabled - key is required
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include 'X-API-Key' header.",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    if api_key not in API_KEYS:
        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    logger.debug(f"Valid API key: {api_key[:8]}...")
    return api_key


async def optional_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Optional API key verification for public endpoints that may have auth.

    Returns the API key if valid, None if not provided or auth disabled.
    Does not raise exceptions for missing keys.

    Args:
        api_key: The API key from X-API-Key header

    Returns:
        The validated API key, or None
    """
    if not is_auth_enabled():
        return None

    if api_key and api_key in API_KEYS:
        return api_key

    return None
