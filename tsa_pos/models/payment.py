from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from ..models import StandardModel
from .meta import Base


class Payment(StandardModel, Base):
    __tablename__ = 'payment'
    partner_id = Column(ForeignKey(
        'partner.id', ondelete='RESTRICT'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255))


class PaymentItems(Base):
    __tablename__ = 'payment_items'

    payment_id = Column(ForeignKey('payment.id', ondelete='CASCADE'),
                        nullable=False, primary_key=True)
    invoice_id = Column(ForeignKey('invoices.id', ondelete='CASCADE'),
                        nullable=False, primary_key=True)
    payment = relationship(
        'Payment', back_populates='payment_items', passive_deletes=True)
    invoice = relationship(
        'Invoices', back_populates='invoice_items', passive_deletes=True)
    amount = Column(Float, nullable=False)
