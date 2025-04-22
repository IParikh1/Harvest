# fastapi_app/api/routes.py
from fastapi import APIRouter, BackgroundTasks
from pipeline.tasks.harvest_jobs import harvest_insight

router = APIRouter()

@router.post("/harvest")
def run_harvest(source: str, query: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(harvest_insight, source, query)
    return {"status": "Harvesting started"}