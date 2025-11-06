# models/tracking.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Float
from sqlalchemy.orm import relationship
from core.database import Base
from utils.timezone import now_ist

class Tracking(Base):
    __tablename__ = "trackings"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False)
    remarks = Column(String(255))
    updated_at = Column(DateTime(timezone=True), default=now_ist, nullable=False)

    task = relationship("Task", back_populates="trackings")
    project = relationship("Project", back_populates="trackings")
