from sqlalchemy import Column, String, Float
from app.database import Base


class InventoryItem(Base):
    __tablename__ = "inventory"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    minThreshold = Column(Float, nullable=False)
