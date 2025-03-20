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
            api = AvitoAPI(account.access_token)

            # Проверка и обновление токена перед отправкой запроса
            if not await check_token_validity(account.access_token):
                logger.info("Токен истек, обновляем...")
                try:
                    new_tokens = await refresh_avito_token(account.refresh_token)
                    account.access_token = new_tokens['access_token']
                    account.refresh_token = new_tokens.get('refresh_token', account.refresh_token)
                    await session.commit()
                except Exception as e:
                    logger.error(f"Ошибка обновления токена для аккаунта {account.id}: {str(e)}")
                    await message.answer("⚠️ Не удалось обновить токен. Пожалуйста, авторизуйтесь снова.")
                    return

            try:
                messages = await api.get_unread_messages()
                for msg in messages:
                    msg['account_name'] = account.account_name
                    all_messages.append(msg)
            except AvitoAPIError as e:
                logger.error(f"Ошибка получения сообщений для аккаунта {account.id}: {str(e)}")
                continue

        if not all_messages:
            return await message.answer("📭 Нет новых сообщений")

        response = []
        for msg in all_messages:
            response.append(
                f"💬 Сообщение ID: {msg['id']}\n"
                f"📩 Сообщение: {msg['content'][:50]}\n"
                f"📩 Сообщение: {msg['content'][:50]}...\n"
                f"📂 Аккаунт: {msg['account_name']}\n"
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
        if "Чат ID: " not in original_text:
            return await message.answer("⚠️ Неверный формат сообщения для ответа.")

        chat_id = original_text.split("Чат ID: ")[1].split("\n")[0].strip()

        result = await session.execute(
            select(AvitoAccount)
            .join(Manager)
            .where(Manager.telegram_id == message.from_user.id)
        )
        account = result.scalars().first()

        if not account:
            return await message.answer("🚫 Аккаунт не найден")

        api = AvitoAPI(account.access_token)

        if not await check_token_validity(account.access_token):
            logger.info("Токен истек, обновляем...")
            new_tokens = await refresh_avito_token(account.refresh_token)
            account.access_token = new_tokens['access_token']
            account.refresh_token = new_tokens.get('refresh_token', account.refresh_token)
            await session.commit()

        await api.send_message(chat_id, message.text)
        await message.answer("✅ Сообщение отправлено")

    except AvitoAPIError as e:
        await message.answer(f"⚠️ Ошибка отправки: {str(e)}")
    except Exception as e:
        logger.error(f"Reply error: {str(e)}")
        await message.answer("🚫 Ошибка обработки ответа")