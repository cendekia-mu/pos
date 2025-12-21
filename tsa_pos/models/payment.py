from base64 import standard_b64encode
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from tsa_pos.models.base import StandardModel
from .meta import Base

class Payment(StandardModel):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255))


class PaymentItem(Base):
    __tablename__ = 'payment_item'

    payment_id = Column(ForeignKey('payment.id', ondelete='CASCADE'), 
                         nullable=False, primary_key=True)
    invoice_id = Column(ForeignKey('invoice.id', ondelete='CASCADE'), 
                         nullable=False, primary_key=True)
    payment = relationship('Payment', back_populates='payment_items', passive_deletes=True)
    invoice = relationship('Invoices', back_populates='invoice_items', passive_deletes=True)
    amount = Column(Float, nullable=False)

