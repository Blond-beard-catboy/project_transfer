from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MonthlyOrdersOut(BaseModel):
    year: int
    month: int
    total_orders: int
    completed_orders: int
    total_revenue: float
    updated_at: datetime

class PopularRoutesOut(BaseModel):
    pickup_location: str
    delivery_location: str
    trips_count: int
    updated_at: datetime

class CustomerStatsOut(BaseModel):
    customer_id: int
    total_orders: int
    avg_order_amount: float
    updated_at: datetime