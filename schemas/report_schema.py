# schemas/report_schema.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class PeriodQuery(BaseModel):
    period: str | None = "day"  # day, week, month, custom
    start_date: date | None = None
    end_date: date | None = None

class ProductivityRow(BaseModel):
    date: date
    user_id: int | None
    user_name: str | None
    tasks_assigned: int
    tasks_completed: int
    completion_rate: float
    work_hours: float

    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    title: str
    rows: List[dict]

class ExportResponse(BaseModel):
    download_path: str

class AISuggestion(BaseModel):
    user_id: int | None
    user_name: str | None
    suggestion: str
    reason: str
