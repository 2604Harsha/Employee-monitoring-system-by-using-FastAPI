from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base
from utils.timezone import now_ist
import enum

class LeaveStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default="Pending")
    # status = Column(Enum(LeaveStatus), default=LeaveStatus.pending)
    applied_on = Column(DateTime(timezone=True), default=now_ist)

    user = relationship("User", backref="leaves")
