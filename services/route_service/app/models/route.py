from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from datetime import datetime

class RouteStatus(str, enum.Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"

class RoutePointType(str, enum.Enum):
    pickup = "pickup"
    delivery = "delivery"
    service = "service"

class RoutePointStatus(str, enum.Enum):
    pending = "pending"
    done = "done"

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=True)  # связь с заказом (опционально)
    status = Column(Enum(RouteStatus), default=RouteStatus.planned)
    created_at = Column(DateTime, default=datetime.utcnow)

    points = relationship("RoutePoint", back_populates="route", cascade="all, delete-orphan")

class RoutePoint(Base):
    __tablename__ = "route_points"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    type = Column(Enum(RoutePointType), nullable=False)
    cargo_id = Column(Integer, nullable=True)  # опционально, если точка связана с грузом
    address = Column(String, nullable=False)
    planned_time = Column(DateTime, nullable=True)
    actual_time = Column(DateTime, nullable=True)
    status = Column(Enum(RoutePointStatus), default=RoutePointStatus.pending)

    route = relationship("Route", back_populates="points")