# fastapi_app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from fastapi_app.api.routes import router, limiter
from fastapi_app.core.config import API_TITLE, API_VERSION, RATE_LIMIT
from fastapi_app.core.auth import is_auth_enabled

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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

# Add rate limiter to app state (required by slowapi)
app.state.limiter = limiter


# Custom rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": "Too many requests. Please try again later.",
            "retry_after": 60
        },
        headers={"Retry-After": "60"}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)
