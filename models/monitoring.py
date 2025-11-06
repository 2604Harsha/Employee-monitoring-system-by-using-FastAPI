from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class EmployeeMonitoring(Base):
    __tablename__ = "employee_monitoring"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    application_used = Column(String, nullable=True)
    website_visited = Column(String, nullable=True)
    idle_time = Column(Integer, default=0)  # in minutes
    active_time = Column(Integer, default=0)  # in minutes
    screenshot_path = Column(String, nullable=True)
    screen_streaming = Column(Boolean, default=False)
    location_mode = Column(String, default="remote")  # remote, hybrid, office
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="monitoring_logs")
