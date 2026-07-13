from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.jobs.models import Job


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_job_by_id(self, job_id: int) -> Job | None:
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        return job

    async def create_job(self, task_type: str, payload: dict) -> Job:
        job = Job(task_type=task_type, payload=payload)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def update_job(self, job: Job) -> Job:
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job
