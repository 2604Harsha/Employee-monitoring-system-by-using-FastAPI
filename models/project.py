from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from utils.timezone import now_ist

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    project_name = Column(String, nullable=False)
    progress = Column(Float, default=0.0)
    status = Column(String, default="Pending")
    remarks = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=now_ist, onupdate=now_ist)

    task = relationship("Task", foreign_keys=[task_id], backref="projects")
    trackings = relationship("Tracking", back_populates="project", cascade="all, delete")
