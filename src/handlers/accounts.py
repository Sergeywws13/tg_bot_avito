# src/handlers/accounts.py
from aiogram import Router, types
from aiogram.filters import Command
from src.database.connector import get_db_pool
from src.utils.crypto import encrypt_token

router = Router()

@router.message(Command("add_account"))
async def add_account(message: types.Message):
    # Запрос токена у пользователя
    await message.answer("Введите токен доступа Авито:")

    # Сохранение токена в БД (пример)
    async with get_db_pool() as pool:
        async with pool.acquire() as conn:
            encrypted_token = encrypt_token("user_token")
            await conn.execute(
                "INSERT INTO avito_accounts (account_name, access_token, manager_id) VALUES ($1, $2, $3)",
                "Мой аккаунт", encrypted_token, message.from_user.id
            )
    await message.answer("Аккаунт успешно добавлен!")
    