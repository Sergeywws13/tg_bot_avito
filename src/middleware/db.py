from aiogram import BaseMiddleware
from src.database.connector import get_db_pool
from main import dp

class DBMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with get_db_pool() as pool:
            data["db"] = pool
            return await handler(event, data)

# Подключить в main.py
dp.middleware.setup(DBMiddleware())