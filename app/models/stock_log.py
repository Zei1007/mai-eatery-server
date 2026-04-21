from sqlalchemy import Column, String, Float, BigInteger
from app.database import Base


class StockLog(Base):
    __tablename__ = "stock_logs"

    id = Column(String, primary_key=True, index=True)
    itemId = Column(String, nullable=False)
    itemName = Column(String, nullable=True)
    itemUnit = Column(String, nullable=True)
    change = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    reason = Column(String, nullable=True)
