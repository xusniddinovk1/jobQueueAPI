from fastapi import APIRouter, Depends, HTTPException, status

from app.jobs.schemas import JobCreateSchema, JobResponseSchema
from app.jobs.service import JobService
from app.jobs.dependencies import get_job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobResponseSchema], status_code=status.HTTP_200_OK)
async def get_jobs(
        job_status: str | None = None,
        limit: int = 10,
        offset: int = 0,
        service: JobService = Depends(get_job_service)
):
    jobs = await service.list_jobs(job_status, limit, offset)
    return jobs


@router.post("/", response_model=JobResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_job(
        job_data: JobCreateSchema,
        service: JobService = Depends(get_job_service)
):
    job = await service.create_job(job_data.task_type, job_data.payload)
    return job


@router.get("/{job_id}", response_model=JobResponseSchema, status_code=status.HTTP_200_OK)
async def get_job(
        job_id: int,
        service: JobService = Depends(get_job_service)
):
    job = await service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
