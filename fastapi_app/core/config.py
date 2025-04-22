# fastapi_app/core/config.py
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='config/.env')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")