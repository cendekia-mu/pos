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
# from .base import DefaultModel
# class Invoices(DefaultModel, Base):
#     __tablename__ = 'invoices'
#     name = Column(String(128))
#     code = Column(String(128))
#     amount = Column(Float)
#     est_delivery = Column(DateTime)
#     invoice_date = Column(DateTime)

#     # created_uid = Column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False,)
#     # updated_uid = Column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=True)
#     partner_id = Column(ForeignKey(
#         'partner.id', ondelete='RESTRICT'), nullable=False)

#     user_created = relationship('User', foreign_keys=['created_uid'], back_populates='invoice_created', passive_deletes=True)
#     user_updated = relationship('User', foreign_keys=['updated_uid'], back_populates='invoice_updated', passive_deletes=True)

#     partner = relationship('Partner', back_populates='invoice', passive_deletes=False)
#     invoice_items = relationship('InvoiceItems', back_populates='invoice')

# class InvoiceItems(Base):
#     __tablename__ = 'invoice_items'
#     id = Column(Integer, primary_key=True)
#     qty = Column(Integer)
#     amount = Column(Float)
#     price = Column(Float)
#     status = Column(SmallInteger)
    
#     invoice_id = Column(ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)
#     product_id = Column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
#     invoice_det_id = Column(ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)

#     invoice_created = relationship('Order',back_populates='invoice_created', foreign_keys=[invoice_id])
#     invoice_det_created = relationship('Order',back_populates='invoice_det_created', foreign_keys=[invoice_det_id])
#     product = relationship('Product', back_populates='invoice_items', passive_deletes=True)


