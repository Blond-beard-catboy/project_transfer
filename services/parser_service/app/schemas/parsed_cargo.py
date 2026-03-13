from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ParsedCargoBase(BaseModel):
    external_id: str
    title: str
    description: Optional[str] = None
    weight: float
    pickup_location: str
    delivery_location: str
    pickup_date: datetime
    delivery_date: datetime
    price: Optional[float] = None
    source: Optional[str] = None

class ParsedCargoCreate(ParsedCargoBase):
    pass

class ParsedCargoOut(ParsedCargoBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)