from sqlalchemy import Column, Integer, String, DateTime, Enum
from app.core.database import Base
import enum
from datetime import datetime

class UserRole(str, enum.Enum):
    driver = "driver"
    dispatcher = "dispatcher"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.driver)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)