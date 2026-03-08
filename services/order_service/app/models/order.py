from sqlalchemy import Column, Integer, String, DateTime, Enum
from app.core.database import Base
import enum
from datetime import datetime

class OrderStatus(str, enum.Enum):
    new = "new"
    confirmed = "confirmed"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    cargo_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, nullable=False)
    driver_id = Column(Integer, nullable=True)
    route_id = Column(Integer, nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.new)
    contract_file = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)