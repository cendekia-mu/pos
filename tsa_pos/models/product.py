from unicodedata import category
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    SmallInteger,
    Column,
    Float,
)

from sqlalchemy.orm import relationship
from tsa_pos.models.base import StandardModel
from .meta import Base

class ProductCategory(StandardModel, Base):
    __tablename__ = 'product_category'
    # id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    product = relationship(
        'Product', back_populates='product_category', passive_deletes=True)


class Product(StandardModel, Base):
    __tablename__ = 'product'
    # id = Column(Integer, primary_key=True)
    name = Column(String(128))
    # status = Column(SmallInteger)
    # created = Column(DateTime)
    # updated = Column(DateTime)
    stock = Column(Integer)
    min_stock = Column(Integer)
    selleable = Column(SmallInteger)

    # created_uid = Column(ForeignKey('users.id', ondelete='CASCADE'),nullable=False)
    # updated_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(ForeignKey(
        'product_category.id', ondelete='CASCADE'), nullable=False)
    product_category = relationship(
        'ProductCategory', back_populates='product', passive_deletes=True)

    # user_created = relationship('User', foreign_keys=[created_uid], back_populates='products_created', passive_deletes=True)
    # user_updated = relationship('User', foreign_keys=[updated_uid], back_populates='products_updated', passive_deletes=True)
    # order_items = relationship('OrderItems', back_populates='product', passive_deletes=True)

class ProductItems(Base):
    __tablename__ = 'product_items'
    product_id = Column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False,primary_key=True)
    item_id = Column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    qty = Column(Float)
    