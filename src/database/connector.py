from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

from src.models.base import Base

class Database:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def create_all(self):
        """Создает все таблицы в базе данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def dispose(self):
        """Закрывает соединения"""
        await self.engine.dispose()

    def session_middleware(self):
        class SessionMiddleware(BaseMiddleware):
            async def __call__(
                self,
                handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
                event: Any,
                data: Dict[str, Any]
            ) -> Any:
                async with self.db.session_factory() as session:
                    data["session"] = session
                    return await handler(event, data)
        
        middleware = SessionMiddleware()
        middleware.db = self
        return middleware


# Инициализация
db = Database("postgresql+asyncpg://avito_user:Av1t0_S3cr3t!@localhost:5433/avito_bot_db")