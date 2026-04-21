from sqlalchemy import Column, String, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    image = Column(String, nullable=True)
    ingredients = relationship(
        "ProductIngredient",
        cascade="all, delete-orphan",
        lazy="joined",
        foreign_keys="ProductIngredient.product_id",
    )
