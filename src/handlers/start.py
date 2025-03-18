from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os

from src.models import Manager, AvitoAccount
from src.services.auth import get_client_credentials_token, exchange_code_for_token
from src.database.connector import db

router = Router()

async def get_or_create_manager(session: AsyncSession, telegram_id: int) -> Manager:
    result = await session.execute(select(Manager).where(Manager.telegram_id == telegram_id))
    manager = result.scalar_one_or_none()
    
    if not manager:
        manager = Manager(telegram_id=telegram_id)
        session.add(manager)
        await session.commit()
    return manager

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    auth_url = (
        f"https://www.avito.ru/oauth?"
        f"response_type=code&"
        f"client_id={os.getenv('AVITO_CLIENT_ID')}&"
        f"scope=messenger:read,messenger:write&"
        f"redirect_uri={os.getenv('AVITO_REDIRECT_URI')}&"
        f"state={message.from_user.id}"
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Авторизоваться через Avito", url=auth_url)]
    ])
    
    await message.answer("Нажмите кнопку ниже, чтобы авторизоваться через Avito:", reply_markup=markup)
