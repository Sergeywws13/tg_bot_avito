from aiogram import Router, types
from aiogram.filters import Command
from src.database.connector import db
from src.utils.crypto import encrypt_token

router = Router()

@router.message(Command("add_account"))
async def add_account(message: types.Message):
    await message.answer("Введите токен доступа Авито:")


    @router.message()
    async def process_token(message: types.Message):
        token = message.text

        async with (await db.get_pool()).acquire() as conn:
            encrypted_token = encrypt_token(token)
            await conn.execute(
                "INSERT INTO avito_accounts (account_name, access_token, manager_id) VALUES ($1, $2, $3)",
                "Мой аккаунт", encrypted_token, message.from_user.id
            )
        await message.answer("✅ Аккаунт успешно добавлен!")
    