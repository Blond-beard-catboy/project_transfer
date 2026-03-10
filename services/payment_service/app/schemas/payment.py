from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.payment import PaymentStatus

class PaymentBase(BaseModel):
    order_id: int
    amount: float
    due_date: Optional[datetime] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    paid_at: Optional[datetime] = None

class PaymentOut(PaymentBase):
    id: int
    status: PaymentStatus
    paid_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)