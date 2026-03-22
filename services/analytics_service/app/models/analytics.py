from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from app.core.database import Base
from datetime import datetime

class MonthlyOrders(Base):
    __tablename__ = "monthly_orders"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PopularRoutes(Base):
    __tablename__ = "popular_routes"

    id = Column(Integer, primary_key=True)
    pickup_location = Column(String, nullable=False)
    delivery_location = Column(String, nullable=False)
    trips_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CustomerStats(Base):
    __tablename__ = "customer_stats"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False, index=True)
    total_orders = Column(Integer, default=0)
    avg_order_amount = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)