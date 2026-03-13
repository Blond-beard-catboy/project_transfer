from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.cargo import CargoStatus

class CargoBase(BaseModel):
    title: str
    description: Optional[str] = None
    weight: float
    pickup_location: str
    delivery_location: str
    pickup_date: datetime
    delivery_date: datetime

class CargoCreate(CargoBase):
    pass

class CargoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = None
    pickup_location: Optional[str] = None
    delivery_location: Optional[str] = None
    pickup_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    status: Optional[CargoStatus] = None

class CargoOut(CargoBase):
    id: int
    owner_id: int
    status: CargoStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)