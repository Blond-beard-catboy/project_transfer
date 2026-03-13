from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CartItemBase(BaseModel):
    cargo_id: int

class CartItemCreate(CartItemBase):
    pass

class CartItemOut(CartItemBase):
    id: int
    user_id: int
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Для возврата расширенной информации о грузе (может пригодиться)
class CartItemWithCargo(CartItemOut):
    cargo_title: Optional[str] = None
    cargo_weight: Optional[float] = None
    pickup_location: Optional[str] = None
    delivery_location: Optional[str] = None