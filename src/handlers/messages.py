from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from src.services.avito_api import AvitoAPI, AvitoAPIError
from src.models import AvitoAccount, AvitoChat, Manager
from datetime import datetime
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("chats"))
async def handle_chats_command(message: Message, session: AsyncSession):
    """Показывает непрочитанные чаты из всех аккаунтов"""
    try:
        # Получаем все аккаунты пользователя
        result = await session.execute(
            select(AvitoAccount)
            .join(Manager)
            .where(Manager.telegram_id == message.from_user.id)
        )
        accounts = result.scalars().all()

        if not accounts:
            return await message.answer("🚫 Нет подключенных аккаунтов")

        # Собираем все непрочитанные чаты из всех аккаунтов
        all_chats = []
        for account in accounts:
            api = AvitoAPI(account.access_token)
            try:
                chats = await api.get_unread_chats()
                for chat in chats:
                    chat['account_name'] = account.account_name  # Добавляем имя аккаунта
                    all_chats.append(chat)
            except AvitoAPIError as e:
                logger.error(f"Ошибка получения чатов для аккаунта {account.id}: {str(e)}")
                continue

        if not all_chats:
            return await message.answer("📭 Нет новых сообщений")

        # Формируем сообщение с чатами
        response = []
        for chat in all_chats:
            last_msg = chat.get('last_message', {})
            response.append(
                f"💬 Чат ID: {chat['id']}\n"
                f"📩 Сообщение: {last_msg.get('content', {}).get('text', '')[:50]}...\n"
                f"👤 Клиент: {chat.get('client_name', 'Неизвестно')}\n"
                f"📞 Телефон: {chat.get('client_phone', 'Неизвестно')}\n"
                f"🕒 Время: {chat['updated']}\n"
                f"📂 Аккаунт: {chat['account_name']}\n"
            )

        await message.answer("Новые сообщения из Avito:\n" + "\n\n".join(response))

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await message.answer("🚫 Внутренняя ошибка")

@router.message(F.reply_to_message)
async def handle_reply(message: Message, session: AsyncSession):
    """Ответить на сообщение"""
    try:
        # Извлекаем chat_id из ответа
        original_text = message.reply_to_message.text
        chat_id = original_text.split("Чат ID: ")[1].split("\n")[0].strip()

        # Получаем аккаунт
        result = await session.execute(
            select(AvitoAccount)
            .join(Manager)
            .where(Manager.telegram_id == message.from_user.id)
        )
        account = result.scalars().first()

        if not account:
            return await message.answer("🚫 Аккаунт не найден")

        api = AvitoAPI(account.access_token)
        await api.send_message(chat_id, message.text)
        await message.answer("✅ Сообщение отправлено")

    except AvitoAPIError as e:
        await message.answer(f"⚠️ Ошибка отправки: {str(e)}")
    except Exception as e:
        logger.error(f"Reply error: {str(e)}")
        await message.answer("🚫 Ошибка обработки ответа")