from sqlalchemy import (
    PrimaryKeyConstraint,
    SmallInteger,
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

class InvoiceCategory(StandardModel, Base):
    __tablename__ = 'invoice_category'
    name = Column(String(128), unique=True)

class Invoices(StandardModel, Base):
    __tablename__ = 'invoices'
    category_id = Column(ForeignKey(
        'invoice_category.id', ondelete='RESTRICT'), nullable=False)
    category = relationship(
        'InvoiceCategory', backref=backref('invoices'))     
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
        'invoices.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(ForeignKey(
        'product.id', ondelete='CASCADE'), nullable=False)
    qty = Column(Integer)
    amount = Column(Float)
    price = Column(Float)
    order_item_id = Column(ForeignKey('order_items.id', ondelete='CASCADE'), nullable=True)
    order_id = Column(ForeignKey('order_items.id', ondelete='CASCADE'), nullable=True)
    status = Column(SmallInteger)
    
    invoice_id = Column(ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    # invoice_det_id = Column(ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)

    # invoice_created = relationship('Order',back_populates='invoice_created', foreign_keys=[invoice_id])
    # invoice_det_created = relationship('Order',back_populates='invoice_det_created', foreign_keys=[invoice_det_id])
    product = relationship('Product', back_populates='invoice_items', passive_deletes=True)
    invoice = relationship('Invoices', back_populates='invoice_items', passive_deletes=True)
    __table_args__ = (
        PrimaryKeyConstraint("invoice_id", "product_id",
                             name="invoice_items_pkey"),
    )



