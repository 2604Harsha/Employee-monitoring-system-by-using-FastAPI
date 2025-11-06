from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Float, String
from sqlalchemy.orm import relationship
from utils.timezone import now_ist
from datetime import datetime
from core.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(DateTime(timezone=True), default=now_ist)
    punch_in = Column(DateTime(timezone=True), nullable=True)
    punch_out = Column(DateTime(timezone=True), nullable=True)
    work_hours = Column(Float, default=0.0)
    is_present = Column(Boolean, default=True)
    status = Column(String, default="Active")  # Active, Absent, On Leave

    user = relationship("User", backref="attendance_records")
