from aiogram import BaseMiddleware
from src.database.connector import db

class DBMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        pool = await db.get_pool()
        async with pool.acquire() as conn:
            data["db_conn"] = conn
            return await handler(event, data)
