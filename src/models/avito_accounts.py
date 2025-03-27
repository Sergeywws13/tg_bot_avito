from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship
from src.models.base import Base

class AvitoAccount(Base):
    __tablename__ = "avito_accounts"

    id = Column(Integer, primary_key=True)
    account_name = Column(String(100), nullable=False)
    access_token = Column(String(1000), nullable=False)
    refresh_token = Column(String(1000))
    expires_at = Column(DateTime(timezone=True))
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    manager = relationship("Manager", back_populates="accounts")