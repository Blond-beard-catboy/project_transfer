from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.route import RouteStatus, RoutePointType, RoutePointStatus

# ---------- RoutePoint ----------
class RoutePointBase(BaseModel):
    type: RoutePointType
    cargo_id: Optional[int] = None
    address: str
    planned_time: Optional[datetime] = None

class RoutePointCreate(RoutePointBase):
    pass

class RoutePointUpdate(BaseModel):
    actual_time: Optional[datetime] = None
    status: Optional[RoutePointStatus] = None

class RoutePointOut(RoutePointBase):
    id: int
    route_id: int
    actual_time: Optional[datetime] = None
    status: RoutePointStatus
    model_config = ConfigDict(from_attributes=True)

# ---------- Route ----------
class RouteBase(BaseModel):
    order_id: Optional[int] = None

class RouteCreate(RouteBase):
    pass

class RouteUpdate(BaseModel):
    status: Optional[RouteStatus] = None
    order_id: Optional[int] = None

class RouteOut(RouteBase):
    id: int
    status: RouteStatus
    created_at: datetime
    points: List[RoutePointOut] = []
    model_config = ConfigDict(from_attributes=True)