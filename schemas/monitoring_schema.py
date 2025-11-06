from pydantic import BaseModel
from datetime import datetime

class MonitoringBase(BaseModel):
    application_used: str | None = None
    website_visited: str | None = None
    idle_time: int | None = 0
    active_time: int | None = 0
    screenshot_path: str | None = None
    screen_streaming: bool | None = False
    location_mode: str | None = "remote"

class MonitoringCreate(MonitoringBase):
    user_id: int

class MonitoringUpdate(MonitoringBase):
    pass

class MonitoringResponse(MonitoringBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
