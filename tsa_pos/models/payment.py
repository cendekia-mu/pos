from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
)
from sqlalchemy.sql import func
from .meta import Base


class Payment(Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
