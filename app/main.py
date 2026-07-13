from fastapi import FastAPI

from app.jobs.router import router as jobs_router

app = FastAPI(title="Task Queue API")

app.include_router(jobs_router)