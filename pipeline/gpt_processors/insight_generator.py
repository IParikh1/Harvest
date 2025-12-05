# pipeline/gpt_processors/insight_generator.py
import logging
from fastapi_app.services.llm_service import run_llm, LLMServiceError

logger = logging.getLogger(__name__)


def generate_insight(source_data: str, query: str) -> str:
    """
    Generate insights from source data based on a query.

    Args:
        source_data: The data to analyze
        query: The question/query about the data

    Returns:
        The LLM-generated insight

    Raises:
        LLMServiceError: If the LLM service fails
    """
    prompt = f"""Analyze the following data and answer the query.

Data:
{source_data}

Query: {query}

Provide a clear, concise analysis based on the data provided."""

    logger.info(f"Generating insight for query: {query[:50]}...")
    result = run_llm(prompt)
    logger.info("Insight generated successfully")
    return result
