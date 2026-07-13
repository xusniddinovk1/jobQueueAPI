from app.redis_client import redis_client
from app.jobs.models import Job
from app.jobs.repository import JobRepository


class JobService:
    def __init__(self, repo: JobRepository):
        self.repo = repo

    async def create_job(self, task_type: str, payload: dict) -> Job:
        job = await self.repo.create_job(task_type, payload)
        await redis_client.rpush("job_queue", str(job.id))
        return job


    async def get_job(self, job_id: int) -> Job | None:
        return await self.repo.get_job_by_id(job_id)