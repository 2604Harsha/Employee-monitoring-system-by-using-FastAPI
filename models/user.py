from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    contact = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    department = Column(String, nullable=True)
    team = Column(String, nullable=True)
    role_name = Column(String, nullable=False)  # Role-based (not ID-based)
    # is_active = Column(Boolean, default=True)



