from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.notification import NotificationStatus

class NotificationBase(BaseModel):
    user_id: int
    type: str
    subject: Optional[str] = None
    body: str

class NotificationCreate(NotificationBase):
    pass

class NotificationOut(NotificationBase):
    id: int
    status: NotificationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)