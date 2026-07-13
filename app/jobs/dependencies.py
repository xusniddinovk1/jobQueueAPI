from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.jobs.repository import JobRepository
from app.jobs.service import JobService


def get_job_repository(session: AsyncSession = Depends(get_db)) -> JobRepository:
    return JobRepository(session)


def get_job_service(repo: JobRepository = Depends(get_job_repository)) -> JobService:
    return JobService(repo)
