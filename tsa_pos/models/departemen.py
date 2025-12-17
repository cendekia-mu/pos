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

class Departemen(StandardModel, Base):
    __tablename__ = 'departemen'
    name = Column(String(128), unique=True)


