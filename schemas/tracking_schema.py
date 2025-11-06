# schemas/tracking_schema.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TrackingBase(BaseModel):
    status: str
    remarks: str | None = None

class TrackingCreate(TrackingBase):
    task_id: int | None = None
    project_id: int | None = None

class TrackingUpdate(TrackingBase):
    pass

class TrackingResponse(TrackingBase):
    id: int
    task_id: int | None
    project_id: int | None
    updated_at: datetime

    class Config:
        from_attributes = True
