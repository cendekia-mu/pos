from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    Float,
    Column,
)
from sqlalchemy.orm import relationship, backref
from .base import StandardModel, Base

from .meta import Base

class ReturnCategory(StandardModel, Base):
    __tablename__ = 'return_category'
    name = Column(String(128), unique=True)

class Returns(StandardModel, Base):
    __tablename__ = 'returns'
    
    category_id = Column(ForeignKey(
        'return_category.id', ondelete='RESTRICT'), nullable=False)
    category = relationship(
        'ReturnCategory', backref=backref('returns'))
    
    invoice_id = Column(ForeignKey(
        'invoices.id', ondelete='RESTRICT'), nullable=True)
    invoice = relationship('Invoices', backref=backref('returns'))
    
    partner_id = Column(ForeignKey(
        'partner.id', ondelete='RESTRICT'), nullable=False)
    partner = relationship('Partner', backref=backref('returns'))
    
    name = Column(String(128))
    code = Column(String(128), unique=True)
    return_date = Column(DateTime)
    total_amount = Column(Float)
    reason = Column(String(255))
    
    return_items = relationship('ReturnItems', back_populates='return_order')

class ReturnItems(Base):
    __tablename__ = 'return_items'
    
    return_id = Column(ForeignKey(
        'returns.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    product_id = Column(ForeignKey(
        'product.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    
    qty = Column(Integer)
    price = Column(Float)
    amount = Column(Float)
    

    return_order = relationship('Returns', back_populates='return_items')
    product = relationship('Product', backref=backref('return_items'))
   
    invoice_item_id = Column(ForeignKey('invoice_items.invoice_id'))