from pydantic import BaseModel
from datetime import datetime

class AttendanceBase(BaseModel):
    date: datetime | None = None
    punch_in: datetime | None = None
    punch_out: datetime | None = None
    work_hours: float | None = 0.0
    is_present: bool | None = True
    status: str | None = "Active"

class AttendanceCreate(BaseModel):
    pass  # Punch-in handled automatically

class AttendanceResponse(AttendanceBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
