from sqlalchemy import (
    Text,
    ForeignKey,
    Integer,
    String,
    DateTime,
    SmallInteger,
    Column
)

from sqlalchemy.orm import relationship

from .meta import Base

class ProductCategory(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)

    product = relationship('Product', back_populates='category', passive_deletes=True)

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_ke=True)
    name = Column(String(128))
    status = Column(SmallInteger)
    created = Column(DateTime)
    updated = Column(DateTime)
    stock = Column(Integer)
    min_stock = Column(Integer)
    selleable = Column(SmallInteger)

    created_uid = Column(ForeignKey('users.id', ondelete='CASCADE'),nullable=False)
    updated_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(ForeignKey('category.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User', back_populates='product', passive_deletes=True)
    category = relationship('Category', back_populates='product', passive_deletes=True)
    order_items = relationship('Order_items', back_populates='product', passive_deletes=True)

class ProductItems(Base):
    __tablename__ = 'product_items'
    product_id = Column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    item_id = Column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    