from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Productivity(Base):
    __tablename__ = "productivity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    application_name = Column(String, nullable=False)
    website_name = Column(String, nullable=True)
    is_productive = Column(Boolean, default=True)
    productive_time = Column(Integer, default=0)  # in minutes
    unproductive_time = Column(Integer, default=0)
    productivity_score = Column(Float, default=0.0)
    category = Column(String, nullable=True)  # e.g., "development", "social media"
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="productivity_logs")
