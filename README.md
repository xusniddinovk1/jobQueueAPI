# job-queue-api

Task/Job Queue API — a self-built background job processing system using FastAPI, SQLAlchemy (async), and Redis, with a custom worker instead of Celery.

---

## Requirements

- Docker
- Docker Compose
- uv

---

## Environment Variables

```bash
cp .env.example .env
# Fill in the required values
```

Key variables:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/task_queue_db
REDIS_URL=redis://redis:6379/0
```

---

## Running the Project

### Docker Compose (Recommended)

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Starts 4 containers: `web`, `worker`, `db` (PostgreSQL), `redis`.

Run migrations:

```bash
docker compose -f docker/docker-compose.yml exec web uv run alembic upgrade head
```

### Native (uv)

```bash
git clone https://github.com/xusniddinovk1/jobQueueAPI
cd jobQueueAPI

uv sync

uv run alembic upgrade head

uv run uvicorn app.main:app --reload
```

Run the worker in a separate terminal:

```bash
uv run python -m app.worker.main
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/jobs/` | Create a new job |
| GET | `/jobs/` | List jobs (supports `job_status`, `limit`, `offset` filters) |
| GET | `/jobs/{job_id}` | Get a single job |

---

## API Documentation

FastAPI generates docs automatically:

```
http://localhost:8000/docs
```

---

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for details on system design, the layered architecture, and how the custom worker replaces Celery.