# fastapi_app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_app.api.routes import router
from fastapi_app.core.config import API_TITLE, API_VERSION

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
    yield
    # Shutdown
    logger.info("Shutting down Harvest API")


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="AI-powered data analysis and insight generation API using Ollama",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)
