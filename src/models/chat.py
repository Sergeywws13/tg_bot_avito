from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class AvitoChat(Base):
    __tablename__ = 'avito_chats'
    
    id = Column(Integer, primary_key=True)
    avito_chat_id = Column(String(50), unique=True)
    last_message = Column(Text)
    client_name = Column(String(100))
    client_phone = Column(String(20))
    last_update = Column(DateTime, default=datetime.utcnow)
    
    account_id = Column(Integer, ForeignKey('avito_accounts.id'))
    manager_id = Column(Integer, ForeignKey('managers.id'))
    
    account = relationship("AvitoAccount", back_populates="chats")
    manager = relationship("Manager", back_populates="chats")