import asyncio
from aiogram import Bot, Dispatcher
from src.middleware.db import DBMiddleware

# Инициализация
bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(bot=bot)

# Подключение middleware
dp.middleware.setup(DBMiddleware())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())