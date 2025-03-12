from sqlalchemy import Column, Integer, String, ForeignKey
from src.models.base import Base

class AvitoAccount(Base):
    __tablename__ = "avito_accounts"

    id = Column(Integer, primary_key=True)
    account_name = Column(String(100), nullable=False)
    access_token = Column(String(200), nullable=False)
    telegram_bot_id = Column(Integer)
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=False)
