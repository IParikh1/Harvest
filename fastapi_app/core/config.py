# fastapi_app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='config/.env')

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

# Optional: OpenAI fallback (if user wants to switch providers)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# API Configuration
API_TITLE = "Harvest API"
API_VERSION = "1.0.0"
