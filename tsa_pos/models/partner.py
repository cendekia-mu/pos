from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
    SmallInteger,
    DateTime,
    Float
)

from sqlalchemy.orm import relationship

from .meta import Base

class Partner(Base):
    __tablename__ = 'partner'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    status = Column(SmallInteger)
    created = Column(DateTime)
    updated = Column(DateTime)
    kode = Column(String(32))
    kelurahan = Column(String(64))
    addres_1 = Column(String(64))
    addres_2 = Column(String(64))
    is_vendor = Column(SmallInteger)
    is_customer = Column(SmallInteger)
    balance = Column(Float)

    created_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    updated_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    provinsi_id = Column(ForeignKey('provinsi.id', ondelete='CASCADE'), nullable=False)
    kota_id = Column(ForeignKey('kota.id', ondelete='CASCADE'), nullable=False)
    kecamatan_id = Column(ForeignKey('kecamatan.id', ondelete='CASCADE'), nullable=False)

    user_created = relationship('User', foreign_keys=[created_uid], back_populates='partner_created', passive_deletes=True)
    user_updated = relationship('User', foreign_keys=[updated_uid], back_populates='partner_updated', passive_deletes=True)
    provinsi = relationship('Provinsi', back_populates='partner', passive_deletes=True)
    kota = relationship('Kota', back_populates='partner', passive_deletes=True)
    kecamatan = relationship('Kecamatan', back_populates='partner', passive_deletes=True)
    order = relationship('Order', back_populates='partner', passive_deletes=True)

