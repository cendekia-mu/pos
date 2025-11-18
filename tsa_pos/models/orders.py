from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    Float,
    Column,
    SmallInteger,
)

from sqlalchemy.orm import relationship, backref
from tsa_pos.models.base import StandardModel, DefaultModel

from .meta import Base

class Orders(StandardModel, Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)

    name = Column(String(128))
    code = Column(String(128))
    amount = Column(Float)
    status = Column(SmallInteger)
    est_delivery = Column(DateTime)
    order_date = Column(DateTime)
    partner_id = Column(ForeignKey('partner.id', ondelete='SET NULL'), nullable=False)
    partner = relationship('Partner', backref=backref("orders"))


class OrderItems(DefaultModel, Base):
    __tablename__ = 'order_items'
    invoice_id = Column(ForeignKey(
        'orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(ForeignKey(
        'product.id', ondelete='RESTRICT'), nullable=False)
    qty = Column(Integer)
    amount = Column(Float)
    price = Column(Float)
    invoiced = Column(Integer)
    product = relationship('Product', backref=backref('product'))


