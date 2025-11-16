# from sqlalchemy import (
#     String,
#     Integer,
#     ForeignKey,
#     DateTime,
#     Float,
#     Column,
#     SmallInteger,
# )

# from sqlalchemy.orm import relationship

# from .meta import Base

# class Order(Base):
#     __tablename__ = 'orders'
#     id = Column(Integer, primary_key=True)
#     name = Column(String(128))
#     code = Column(String(128))
#     amount = Column(Float)
#     status = Column(SmallInteger)
#     created = Column(DateTime)
#     updated = Column(DateTime)
#     est_delivery = Column(DateTime)
#     order_date = Column(DateTime)

#     created_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False,)
#     updated_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
#     partner_id = Column(ForeignKey('partner.id', ondelete='CASCADE'), nullable=False)

#     user_created = relationship('User', foreign_keys=[created_uid], back_populates='order_created', passive_deletes=True)
#     user_updated = relationship('User', foreign_keys=[updated_uid], back_populates='order_updated', passive_deletes=True)

#     partner = relationship('Partner', back_populates='order', passive_deletes=True)
#     invoice_created = relationship('OrderItems',back_populates='order_created', foreign_keys="[OrderItems.invoice_id]")
#     invoice_det_created = relationship('OrderItems', back_populates='order_det_created', foreign_keys="[OrderItems.order_det_id]")

# class OrderItems(Base):
#     __tablename__ = 'order_items'
#     id = Column(Integer, primary_key=True)
#     qty = Column(Integer)
#     amount = Column(Float)
#     price = Column(Float)
#     status = Column(SmallInteger)
    
#     invoice_id = Column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
#     product_id = Column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
#     order_det_id = Column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)

#     order_created = relationship('Order',back_populates='invoice_created', foreign_keys=[invoice_id])
#     order_det_created = relationship('Order',back_populates='invoice_det_created', foreign_keys=[order_det_id])
#     product = relationship('Product', back_populates='order_items', passive_deletes=True)


