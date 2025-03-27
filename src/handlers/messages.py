from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.services.auth import check_token_validity, refresh_avito_token
from src.services.avito_api import AvitoAPI, AvitoAPIError
from src.models import AvitoAccount, Manager

import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("messages"))
async def handle_chats_command(message: Message, session: AsyncSession):
    """Показывает непрочитанные сообщения из всех аккаунтов"""
    try:
        result = await session.execute(
            select(AvitoAccount)
            .join(Manager)
            .where(Manager.telegram_id == message.from_user.id)
        )
        accounts = result.scalars().all()

        if not accounts:
            return await message.answer("🚫 Нет подключенных аккаунтов")

        all_messages = []
        for account in accounts:
            # Проверка и обновление токена перед созданием API
            if not await check_token_validity(account.access_token):
                logger.info("Токен истек, обновляем...")
                try:
                    new_tokens = await refresh_avito_token(account.refresh_token, account.id)
                    account.access_token = new_tokens['access_token']
                    account.refresh_token = new_tokens.get('refresh_token', account.refresh_token)
                    await session.commit()
                except Exception as e:
                    logger.error(f"Ошибка обновления токена: {str(e)}")
                    await message.answer("⚠️ Не удалось обновить токен")
                    continue

            # Создаем API с актуальным токеном
            api = AvitoAPI(account.access_token)

            try:
                # Получаем чаты с непрочитанными сообщениями
                chats = (await api.get_unread_chats()).get("chats", [])
                for chat in chats:
                    messages = (await api.get_unread_messages(chat["id"])).get("messages", [])
                    for msg in messages:
                        all_messages.append({
                            "content": msg.get("text", "Нет текста"),
                            "chat_id": chat["id"],
                            "account": account.account_name
                        })

            except AvitoAPIError as e:
                logger.error(f"Ошибка API: {str(e)}")
                continue

        if not all_messages:
            return await message.answer("📭 Нет новых сообщений")

        response = [
            f"💬 Чат ID: {msg['chat_id']}\n"
            f"📩 {msg['content'][:100]}\n"
            f"🔗 Аккаунт: {msg['account']}\n"
            for msg in all_messages
        ]

        await message.answer("📨 Непрочитанные сообщения:\n\n" + "\n\n".join(response))

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}", exc_info=True)
        await message.answer("🚫 Произошла ошибка")


@router.message(F.reply_to_message)
async def handle_reply(message: Message, session: AsyncSession):
    try:
        # Извлекаем chat_id из текста сообщения
        original = message.reply_to_message.text
        chat_id = None
        for line in original.split("\n"):
            if line.startswith("💬 Чат ID: "):
                chat_id = line.split("💬 Чат ID: ")[1].strip()
                break
        
        if not chat_id:
            return await message.answer("❌ Неверный формат сообщения")

        # Получаем аккаунт
        result = await session.execute(
            select(AvitoAccount)
            .join(Manager)
            .where(Manager.telegram_id == message.from_user.id)
        )
        account = result.scalars().first()

        if not account:
            return await message.answer("❌ Аккаунт не найден")

        # Обновляем токен при необходимости
        api = AvitoAPI(account.access_token)
        if not await check_token_validity(account.access_token):
            new_tokens = await refresh_avito_token(account.refresh_token)
            account.access_token = new_tokens['access_token']
            account.refresh_token = new_tokens.get('refresh_token', account.refresh_token)
            await session.commit()

        # Отправляем сообщение
        await api.send_message(chat_id, message.text)
        await message.answer("✅ Ответ отправлен")

    except AvitoAPIError as e:
        await message.answer(f"❌ Ошибка Avito: {str(e)}")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await message.answer("🚫 Внутренняя ошибка")

        