from sqlalchemy import (
    ForeignKey,
    String,
    Column,
    Integer,
    Text,
)

from sqlalchemy.orm import relationship
from tsa_pos.models.base import StandardModel
from .meta import Base


class ReturnItem(StandardModel, Base):
    __tablename__ = 'return_item'

    # Relasi utama
    order_id = Column(ForeignKey('order.id'), nullable=False)
    product_id = Column(ForeignKey('product.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)

    # Detail retur
    quantity = Column(Integer, nullable=False)
    reason = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)

    # Kondisi barang
    item_condition = Column(String(64))       # baru / sudah dipakai
    packaging_condition = Column(String(64))  # utuh / rusak

    # Jenis retur
    return_type = Column(String(64))           # refund / exchange
    refund_method = Column(String(64))         # bank / e-wallet
    refund_account = Column(String(128))

    # Status proses
    status = Column(String(64), default='submitted')
    admin_note = Column(Text)

    # Relasi ORM
    order = relationship('Order')
    product = relationship('Product')
    user = relationship('User')
