from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.models.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    avito_account_id = Column(Integer, ForeignKey("avito_accounts.id"), nullable=False)
    message_text = Column(String(1000), nullable=False)
    sender_contacts = Column(String(100))
    direction = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    