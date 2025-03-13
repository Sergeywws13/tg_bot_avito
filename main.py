import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiohttp import web
from src.handlers import start, accounts, auth
from src.middleware.db import DBMiddleware
from src.services.scheduler import check_new_messages
from src.database.connector import db
from src.config import BOT_TOKEN


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def on_startup():
    """Функция, которая выполняется при запуске бота."""
    logger.info("Бот запускается...")
    await db.create_pool()
    logger.info("Пул подключений к базе данных создан.")

async def on_shutdown():
    """Функция, которая выполняется при остановке бота."""
    logger.info("Бот останавливается...")
    await db.get_pool().close()
    logger.info("Пула подключений к базе данных закрыт.")

async def handle_callback(request: web.Request):
    """
    Обрабатывает HTTP-запрос от Flask-сервера.
    """
    data = await request.json()  # Получаем JSON-данные из запроса
    code = data.get("code")  # Извлекаем код авторизации

    if code:
        logger.info(f"Получен код авторизации: {code}")
        # Здесь можно передать код боту (например, через очередь или глобальную переменную)
        # В данном примере просто логируем код
        return web.Response(text="Код получен и передан боту.")
    else:
        logger.error("Код авторизации отсутствует в запросе.")
        return web.Response(text="Ошибка: код отсутствует.", status=400)

async def main():
    """Основная функция для запуска бота и HTTP-сервера."""
    try:
        logger.info("Инициализация бота...")
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(bot=bot)
        
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        dp.update.middleware(DBMiddleware())
        
        dp.include_router(start.router)
        dp.include_router(accounts.router)
        dp.include_router(auth.router)
        
        asyncio.create_task(check_new_messages())
        

        app = web.Application()
        app.router.add_post("/handle_callback", handle_callback)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 5000)
        await site.start()
        
        logger.info("HTTP-сервер запущен на http://localhost:5000")
        logger.info("Бот запущен и готов к работе.")
        
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}", exc_info=True)
    finally:
        logger.info("Бот завершил работу.")

if __name__ == "__main__":
    asyncio.run(main())
