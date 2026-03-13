from sqlalchemy import Column, Integer, DateTime, UniqueConstraint
from app.core.database import Base
from datetime import datetime

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    cargo_id = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    # Ограничение: один пользователь может добавить один груз только один раз
    __table_args__ = (UniqueConstraint('user_id', 'cargo_id', name='unique_user_cargo'),)