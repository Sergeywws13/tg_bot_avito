import asyncio
from datetime import datetime, timedelta
import logging
from aiogram import Bot, Dispatcher
from aiohttp import web
from sqlalchemy import select
from src.handlers import start, messages, commands
from src.middleware.db import DBMiddleware
from src.database.connector import db
from src.config import BOT_TOKEN
from sqlalchemy.ext.asyncio import AsyncSession 
from src.models.avito_accounts import AvitoAccount
from src.models.manager import Manager
from src.services.auth import exchange_code_for_token
from src.services.scheduler import token_refresher


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_or_create_manager(session: AsyncSession, telegram_id: int) -> Manager:
    result = await session.execute(select(Manager).where(Manager.telegram_id == telegram_id))
    manager = result.scalar_one_or_none()
    
    if not manager:
        manager = Manager(telegram_id=telegram_id)
        session.add(manager)
        await session.commit()
    return manager


async def on_startup():
    logger.info("Бот запускается...")
    await token_refresher.start()    
    await db.create_all()


async def on_shutdown():
    logger.info("Бот останавливается...")
    await token_refresher.stop()
    await db.dispose()


async def handle_callback(request: web.Request):
    try:
        query = request.query
        code = query.get("code")
        state = query.get("state")

        if not code or not state:
            return web.Response(text="Missing code or state parameters", status=400)

        logger.info(f"Received code: {code}, state: {state}")

        token_data = await exchange_code_for_token(code)

        async with db.session_factory() as session:
            manager = await get_or_create_manager(session, int(state))

            account = AvitoAccount(
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token', ''),
                expires_at=datetime.now() + timedelta(seconds=token_data['expires_in']),
                manager_id=manager.id,
                account_name="Авторизация через OAuth"
            )
            session.add(account)
            await session.commit()

        bot = request.app['bot']
        await bot.send_message(
            chat_id=state,
            text="✅ Аккаунт Avito успешно привязан!\nТеперь вы можете получать уведомления."
        )

        return web.Response(text="Авторизация завершена! Вернитесь в бот.")

    except Exception as e:
        logger.error(f"Callback handler error: {str(e)}", exc_info=True)
        return web.Response(text=f"Error: {str(e)}", status=500)


async def main():
    """Основная функция для запуска бота и HTTP-сервера."""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot=bot)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DBMiddleware())

    dp.include_router(start.router)
    dp.include_router(messages.router)
    dp.include_router(commands.router)

    app = web.Application()
    app['bot'] = bot
    app.router.add_get("/callback", handle_callback)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

    logger.info("HTTP-сервер запущен на http://0.0.0.0:5000")
    await dp.start_polling(bot)    

if __name__ == "__main__":
    asyncio.run(main())
