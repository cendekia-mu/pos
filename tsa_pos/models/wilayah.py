from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
)

from . import StandardModel
from sqlalchemy.orm import relationship
from .meta import Base


class Provinsi(StandardModel, Base):
    __tablename__ = 'provinsi'
    name = Column(String(128))
    # status = Column(SmallInteger)
    # created = Column(DateTime)
    # updated = Column(DateTime)

    # created_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    # updated_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # user_created = relationship('User', foreign_keys=["created_uid"], back_populates='provinsi_created', passive_deletes=True)
    # user_updated = relationship('User', foreign_keys=["updated_uid"], back_populates='provinsi_updated', passive_deletes=True)
    # kota = relationship('Kota', back_populates='provinsi', passive_deletes=True)
    partner = relationship('Partner', back_populates='provinsi', passive_deletes=True)


class Kota(StandardModel, Base):
    __tablename__ = 'kota'
    # id = Column(Integer, primary_key=True)
    name = Column(String(128))
    # status = Column(SmallInteger)
    # created = Column(DateTime)
    # updated = Column(DateTime)

    # created_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    # updated_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    provinsi_id = Column(ForeignKey(
        'provinsi.id', ondelete='CASCADE'), nullable=False)

    # user_created = relationship('User', foreign_keys=[created_uid], back_populates='kota_created', passive_deletes=True)
    # user_updated = relationship('User', foreign_keys=[updated_uid], back_populates='kota_updated', passive_deletes=True)

    # provinsi = relationship('Provinsi', back_populates='kota', passive_deletes=True)
    # kecamatan = relationship('Kecamatan', back_populates='kota', passive_deletes=True)
    partner = relationship('Partner', back_populates='kota', passive_deletes=True)


class Kecamatan(StandardModel, Base):
    __tablename__ = 'kecamatan'
    # id = Column(Integer, primary_key=True)
    name = Column(String(128))
    # status = Column(SmallInteger)
    # created = Column(DateTime)
    # updated = Column(DateTime)

    # created_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    # updated_uid = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    kota_id = Column(ForeignKey('kota.id', ondelete='CASCADE'), nullable=False)

    # user_created = relationship('User', foreign_keys=[created_uid], back_populates='kecamatan_created', passive_deletes=True)
    # user_updated = relationship('User', foreign_keys=[updated_uid], back_populates='kecamatan_updated', passive_deletes=True)
    # kota = relationship('Kota', back_populates='kecamatan', passive_deletes=True)
    partner = relationship('Partner', back_populates='kecamatan', passive_deletes=True)
