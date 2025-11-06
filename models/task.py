
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from core.database import Base
from utils.timezone import now_ist

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_ist)
    due_date = Column(DateTime(timezone=True), nullable=True)
    progress = Column(Float, default=0.0)  # 0-100
    status = Column(String, default="Pending")  # Pending / In Progress / Completed

    creator = relationship("User", foreign_keys=[created_by], backref="created_tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_tasks")
    trackings = relationship("Tracking", back_populates="task", cascade="all, delete")
