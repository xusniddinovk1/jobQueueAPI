import asyncio

from app.database import async_session_maker
from app.jobs.repository import JobRepository
from app.jobs.models import Job
from app.redis_client import redis_client


async def process_job(job: Job) -> None:
    """Job turiga qarab, tegishli logikani bajaradi."""
    if job.task_type == "resize_image":
        # hozircha oddiy simulyatsiya
        await asyncio.sleep(2)
        return {"message": "Image resized successfully"}

    raise ValueError(f"Unknown task_type: {job.task_type}")


async def worker_loop() -> None:
    print("Worker started, waiting for jobs...")

    while True:
        try:
            result = await redis_client.blpop("job_queue", timeout=5)
        except TimeoutError:
            continue

        if result is None:
            continue  # hech narsa kelmadi, yana kutamiz

        _, job_id_str = result  # blpop ("key_name", "value") qaytaradi
        job_id = int(job_id_str)

        print(f"Processing job {job_id}...")

        async with async_session_maker() as session:
            repo = JobRepository(session)
            job = await repo.get_job_by_id(job_id)

            if not job:
                print(f"Job {job_id} not found")
                continue

            job.status = Job.JobStatus.RUNNING
            await repo.update_job(job)

            try:
                Job_result = await process_job(job)
                job.status = Job.JobStatus.SUCCESS
                job.result = Job_result
            except Exception as e:
                job.status = Job.JobStatus.FAILED
                job.error_message = f"Job {job_id} failed with error: {e}"
            await repo.update_job(job)


if __name__ == "__main__":
    asyncio.run(worker_loop())
