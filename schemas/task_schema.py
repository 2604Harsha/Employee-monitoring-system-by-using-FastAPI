
from pydantic import BaseModel
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    assigned_to: int | None = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    assigned_to: int | None = None
    progress: float | None = None
    status: str | None = None

class TaskResponse(TaskBase):
    id: int
    created_by: int | None
    created_at: datetime
    progress: float
    status: str

    class Config:
        from_attributes = True
