from sqlalchemy import (
    ForeignKey,
    String,
    Column,
)

from sqlalchemy.orm import relationship
from tsa_pos.models.base import StandardModel
from .meta import Base


class Coa(StandardModel, Base):
    __tablename__ = 'coa'
    name = Column(String(128))
    code = Column(String(128), unique=True)
    parent_id = Column(ForeignKey(
        'coa.id', ondelete='CASCADE'), nullable=True)
    parent = relationship(
        'Coa', remote_side='Coa.id', back_populates='children', passive_deletes=True)
    children = relationship(
        'Coa', back_populates='parent', passive_deletes=True)
    
