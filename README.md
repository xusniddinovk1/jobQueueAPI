# Architecture

## Purpose

A background job processing system built to understand how tools like Celery work internally. Instead of using Celery or arq, the queue and worker are built from scratch using Redis lists and a Python asyncio loop.

## Tech Stack

- **Framework**: FastAPI (async)
- **ORM**: SQLAlchemy 2.0 (async, with `Mapped`/`mapped_column`)
- **Database**: PostgreSQL (asyncpg driver)
- **Migrations**: Alembic (async-configured)
- **Queue**: Redis (list-based, `rpush`/`blpop`)
- **Validation**: Pydantic v2
- **Containerization**: Docker + Docker Compose
- **Dependency Manager**: uv

## Layered Architecture

```
Router → Schema → Service → Repository → Model
```

- **Router** — handles HTTP request/response, FastAPI auto-generates docs from it
- **Schema** (Pydantic) — validates input, shapes output (equivalent of DRF serializers)
- **Service** — business logic (pushing jobs to the queue, checking retry limits)
- **Repository** — database operations only, no business logic
- **Model** (SQLAlchemy) — table structure

## Dependency Injection

FastAPI's built-in `Depends()` replaces the manually-written `container.py` pattern used in Django projects:

```python
def get_job_repository(session: AsyncSession = Depends(get_db)) -> JobRepository:
    return JobRepository(session)

def get_job_service(repo: JobRepository = Depends(get_job_repository)) -> JobService:
    return JobService(repo)
```

Each function declares what it needs, and FastAPI resolves the chain automatically when a request comes in.

## Job Flow

```
POST /jobs/
      ↓
Router validates request (JobCreateSchema)
      ↓
Service creates Job (status=PENDING), saves to DB
      ↓
Service pushes job.id to Redis list "job_queue"
      ↓
API returns 201 immediately
      ↓ (background, separate process)
Worker: blpop("job_queue") → picks up job.id
      ↓
Worker loads job from DB, sets status=RUNNING
      ↓
Worker executes the task based on task_type
      ↓
Success → status=SUCCESS, result saved
Failure → retry_count += 1, re-queued with backoff, or status=FAILED after max_retries
```

## Why Redis Lists Instead of Polling

The worker uses `blpop`, a blocking pop — it waits for a job to appear instead of repeatedly checking the queue every few seconds. This avoids wasted requests to Redis and picks up new jobs with no delay.

## Retry Mechanism

On failure, the job is not immediately marked as failed. Instead:

```python
job.retry_count += 1

if job.retry_count < job.max_retries:
    job.status = Job.JobStatus.PENDING
    await asyncio.sleep(2 ** job.retry_count)   # exponential backoff
    await redis_client.rpush("job_queue", str(job.id))
else:
    job.status = Job.JobStatus.FAILED
```

This mirrors Celery's `self.retry(countdown=...)` pattern, built manually. One known limitation: since the worker runs as a single sequential loop, `asyncio.sleep()` during a retry blocks it from picking up other jobs during that wait. Production-grade systems use a separate delayed queue or scheduler to avoid this; this project keeps the simpler version for clarity.

## Async Throughout

Every layer (router, service, repository) uses `async def` / `await`, since the database driver (`asyncpg`) and Redis client are both async. This lets the API handle many concurrent requests without blocking on I/O.

## Database vs Redis

Redis only stores the job ID — never the full job data. The database is always the source of truth. The worker re-fetches the job from the database after receiving its ID from Redis, so it always works with the current state.
