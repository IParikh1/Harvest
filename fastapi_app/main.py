# fastapi_app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi_app.api.routes import router
from fastapi_app.core.config import API_TITLE, API_VERSION, RATE_LIMIT
from fastapi_app.core.auth import is_auth_enabled

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_rate_limit_key(request: Request) -> str:
    """
    Get the key for rate limiting.
    Uses API key if provided, otherwise falls back to IP address.
    """
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    return get_remote_address(request)


# Initialize rate limiter
limiter = Limiter(key_func=get_rate_limit_key)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    logger.info("Using Ollama as LLM provider")
    logger.info(f"Rate limiting: {RATE_LIMIT}")
    logger.info(f"Authentication: {'enabled' if is_auth_enabled() else 'disabled'}")
    yield
    # Shutdown
    logger.info("Shutting down Harvest API")


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="AI-powered data analysis and insight generation API using Ollama",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter

# Custom rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": str(exc.detail),
            "retry_after": exc.detail
        },
        headers={"Retry-After": str(60)}  # Suggest retry after 60 seconds
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)


# Apply rate limiting to specific routes
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Apply rate limiting middleware.
    Skips rate limiting for health check endpoint.
    """
    # Skip rate limiting for health check
    if request.url.path in ["/health", "/auth/status", "/docs", "/openapi.json"]:
        return await call_next(request)

    # Apply rate limit
    try:
        await limiter._check_request_limit(request, None, RATE_LIMIT)
    except RateLimitExceeded as e:
        return await rate_limit_handler(request, e)

    response = await call_next(request)

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = RATE_LIMIT
    return response
