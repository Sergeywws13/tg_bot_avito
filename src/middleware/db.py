from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connector import db
import logging

logger = logging.getLogger(__name__)

class DBMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with db.session_factory() as session:
            data["session"] = session
            try:
                return await handler(event, data)
            finally:
                await session.close()