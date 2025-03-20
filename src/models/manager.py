from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from src.models.base import Base

class Manager(Base):
    __tablename__ = "managers"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)

    accounts = relationship("AvitoAccount", back_populates="manager", cascade="all, delete-orphan")
    