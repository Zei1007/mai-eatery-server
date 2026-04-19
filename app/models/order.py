from sqlalchemy import Column, String, Float, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    total = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    productId = Column(String, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
