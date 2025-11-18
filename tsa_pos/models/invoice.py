from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    Float,
    Column,
)

from sqlalchemy.orm import relationship, backref
from .base import StandardModel, DefaultModel

from .meta import Base

class Invoices(StandardModel, Base):
    __tablename__ = 'invoices'
    name = Column(String(128))
    code = Column(String(128))
    amount = Column(Float)
    est_delivery = Column(DateTime)
    invoice_date = Column(DateTime)
    partner_id = Column(ForeignKey(
        'partner.id', ondelete='RESTRICT'), nullable=False)
    partner = relationship('Partner', backref=backref('invoices'))
    invoice_items = relationship('InvoiceItems', back_populates='invoice')

class InvoiceItems(Base):
    __tablename__ = 'invoice_items'
    invoice_id = Column(ForeignKey(
        'invoices.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    product_id = Column(ForeignKey(
        'product.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    qty = Column(Integer)
    amount = Column(Float)
    price = Column(Float)
    order_item_id = Column(ForeignKey('order_items.id', ondelete='CASCADE'), nullable=True)
    order_id = Column(ForeignKey('order_items.id', ondelete='CASCADE'), nullable=True)
    product = relationship('Product', back_populates='invoice_items', passive_deletes=True)
    invoice = relationship('Invoices', back_populates='invoice_items', passive_deletes=True)


