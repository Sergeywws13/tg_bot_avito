from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Добро пожаловать! Используйте для подключения аккаунта Авито: /add_account\n"
    "Для авторизации используйте /auth")