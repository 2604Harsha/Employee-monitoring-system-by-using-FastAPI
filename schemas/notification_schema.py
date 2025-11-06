# schemas/notification_schema.py
from pydantic import BaseModel
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: int | None
    task_id: int | None
    title: str
    message: str | None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
