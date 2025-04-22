# insight_generator.py
from fastapi_app.services.gpt_service import run_gpt

def generate_insight(source_data: str, query: str):
    prompt = f"Analyze this data:\n{source_data}\n\nBased on the query: {query}"
    return run_gpt(prompt)
    