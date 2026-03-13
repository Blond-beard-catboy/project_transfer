from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey
from app.core.database import Base
import enum
from datetime import datetime

class CargoStatus(str, enum.Enum):
    new = "new"
    booked = "booked"
    in_transit = "in_transit"
    delivered = "delivered"

class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    weight = Column(Float, nullable=False)
    pickup_location = Column(String, nullable=False)
    delivery_location = Column(String, nullable=False)
    pickup_date = Column(DateTime, nullable=False)
    delivery_date = Column(DateTime, nullable=False)
    owner_id = Column(Integer, nullable=False)  # ID владельца из User Service
    status = Column(Enum(CargoStatus), default=CargoStatus.new)
    created_at = Column(DateTime, default=datetime.utcnow)