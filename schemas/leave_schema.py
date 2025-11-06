from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class LeaveStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class LeaveBase(BaseModel):
    start_date: datetime
    end_date: datetime
    reason: str

class LeaveCreate(LeaveBase):
    pass

class LeaveUpdate(BaseModel):
    status: LeaveStatus

class LeaveResponse(LeaveBase):
    id: int
    user_id: int
    status: LeaveStatus
    applied_on: datetime

    class Config:
        orm_mode = True
