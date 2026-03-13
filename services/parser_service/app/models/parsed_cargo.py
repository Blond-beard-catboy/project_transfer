from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base
from datetime import datetime

class ParsedCargo(Base):
    __tablename__ = "parsed_cargos"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    weight = Column(Float, nullable=False)
    pickup_location = Column(String, nullable=False)
    delivery_location = Column(String, nullable=False)
    pickup_date = Column(DateTime, nullable=False)
    delivery_date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=True)        # предлагаемая цена
    source = Column(String, nullable=True)      # источник данных
    created_at = Column(DateTime, default=datetime.utcnow)