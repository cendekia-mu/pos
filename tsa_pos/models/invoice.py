from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    Float,
    Column,
    SmallInteger,
)

from sqlalchemy.orm import relationship

from .meta import Base

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    code = Column(String(128))
    amount = Column(Float)
    status = Column(SmallInteger)
    created = Column(DateTime)
    updated = Column(DateTime)
    est_delivery = Column(DateTime)
    order_date = Column(DateTime)

    created_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    updated_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    partner_id = Column(ForeignKey('partner.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User', back_populates='order', passive_deletes=True)
    partner = relationship('Partner', back_populates='order', passive_deletes=True)
    order_items = relationship('Order_items', back_populates='order', passive_deletes=True)

class OrderItems(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    qty = Column(Integer)
    amount = Column(Float)
    price = Column(Float)
    status = Column(SmallInteger)
    
    invoice_id = Column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    order_det_id = Column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)

    order = relationship('Order', back_populates='order_items', passive_deletes=True)
    product = relationship('Product', back_populates='order_items', passive_deletes=True)


