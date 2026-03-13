from sqlalchemy import Column, Integer, String, DateTime, Enum
from app.core.database import Base
import enum
from datetime import datetime

class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # email, sms
    subject = Column(String)
    body = Column(String, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)