# models/departemen.py
from sqlalchemy import Column, String, Integer
from tsa_pos.models.base import StandardModel


class Departemen(StandardModel, Base):
    __tablename__ = "departemen"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
