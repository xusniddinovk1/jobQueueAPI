from datetime import datetime
from pydantic import BaseModel


class JobCreateSchema(BaseModel):
    task_type: str
    payload: dict


class JobResponseSchema(BaseModel):
    id: int
    task_type: str
    payload: dict
    status: str
    result: dict | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
