from pydantic import BaseModel
from datetime import datetime

class ProductivityBase(BaseModel):
    application_name: str
    website_name: str | None = None
    is_productive: bool = True
    productive_time: int = 0
    unproductive_time: int = 0
    category: str | None = None

class ProductivityCreate(ProductivityBase):
    user_id: int

class ProductivityUpdate(ProductivityBase):
    pass

class ProductivityResponse(ProductivityBase):
    id: int
    user_id: int
    productivity_score: float
    timestamp: datetime

    class Config:
        orm_mode = True
