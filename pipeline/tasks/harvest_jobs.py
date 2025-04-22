# pipeline/tasks/harvest_jobs.py
from celery import Celery
from pipeline.gpt_processors.insight_generator import generate_insight

celery_app = Celery("harvest_tasks", broker="redis://localhost:6379/0")

@celery_app.task
def harvest_insight(source: str, query: str):
    result = generate_insight(source, query)
    print("Insight harvested:\n", result)
    return result