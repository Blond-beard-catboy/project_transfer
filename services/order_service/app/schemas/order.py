from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.order import OrderStatus

class OrderBase(BaseModel):
    cargo_id: int
    customer_id: int
    driver_id: Optional[int] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    driver_id: Optional[int] = None
    route_id: Optional[int] = None

class OrderOut(OrderBase):
    id: int
    route_id: Optional[int] = None
    status: OrderStatus
    contract_file: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)