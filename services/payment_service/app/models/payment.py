from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from app.core.database import Base
import enum
from datetime import datetime

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    cancelled = "cancelled"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)  # ID заказа из Order Service
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    due_date = Column(DateTime, nullable=True)   # срок оплаты
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)