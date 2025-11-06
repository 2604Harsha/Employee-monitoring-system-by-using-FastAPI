# schemas/project_schema.py
from pydantic import BaseModel
from datetime import datetime

class ProjectBase(BaseModel):
    project_name: str | None = None
    progress: float | None = None
    status: str | None = None
    remarks: str | None = None

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    task_id: int
    updated_at: datetime

    class Config:
        from_attributes = True
