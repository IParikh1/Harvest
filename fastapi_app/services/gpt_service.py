# services/gpt_service.py
import openai
from fastapi_app.core.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def run_gpt(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message["content"]