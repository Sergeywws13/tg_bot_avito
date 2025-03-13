import os
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.services.auth import get_access_token
from src.utils.crypto import encrypt_token
from src.database.connector import db

router = Router()


@router.message(Command("auth"))
async def start_auth(message: types.Message):
    """
    Обрабатывает команду /auth и отправляет пользователю кнопку для авторизации через Авито.
    """
    # Формируем ссылку для авторизации
    auth_url = (
        "https://avito.ru/oauth?"
        f"client_id={os.getenv('CLIENT_ID')}&"  # Используем CLIENT_ID из переменных окружения
        f"response_type=code&"
        f"redirect_uri={os.getenv('REDIRECT_URI')}"  # Используем REDIRECT_URI из переменных окружения
    )

    # Создаем кнопку с ссылкой
    builder = InlineKeyboardBuilder()
    builder.button(text="Авторизоваться через Авито", url=auth_url)
    builder.adjust(1)

    await message.answer(
        "🔑 Для работы с Авито необходимо авторизоваться. Нажмите кнопку ниже:",
        reply_markup=builder.as_markup(),
    )


@router.message(Command("handle_callback"))
async def handle_callback(message: types.Message):
    """
    Обрабатывает код авторизации, полученный от Flask-сервера.
    """
    code = message.text 

    try:
        tokens = await get_access_token(code)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]


        encrypted_token = encrypt_token(access_token)


        async with (await db.get_pool()).acquire() as conn:
            await conn.execute(
                "INSERT INTO avito_accounts (account_name, access_token, refresh_token, manager_id) "
                "VALUES ($1, $2, $3, $4)",
                "Аккаунт пользователя", encrypted_token, refresh_token, message.from_user.id
            )

        await message.answer("✅ Авторизация прошла успешно! Токен сохранен.")
    except Exception as e:
        await message.answer(f"❌ Ошибка авторизации: {e}")
        