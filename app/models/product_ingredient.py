import uuid
from sqlalchemy import Column, String, Float, ForeignKey
from app.database import Base


class ProductIngredient(Base):
    __tablename__ = "product_ingredients"

    id = Column(String, primary_key=True, default=lambda: f"pi-{uuid.uuid4().hex[:8]}")
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    inventory_item_id = Column(String, nullable=False)
    inventory_item_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
