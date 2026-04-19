from sqlalchemy import Column, String, BigInteger
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    action = Column(String, nullable=False)
    details = Column(String, nullable=False)
    user = Column(String, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    type = Column(String, nullable=False)
