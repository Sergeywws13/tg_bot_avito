import aiohttp
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.config import AVITO_CLIENT_SECRET
from src.models.avito_accounts import AvitoAccount
from src.services.avito_api import AvitoAPI, AvitoAPIError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def exchange_code_for_token(code: str) -> dict:
    url = "https://api.avito.ru/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("AVITO_CLIENT_ID"),
        "client_secret": os.getenv("AVITO_CLIENT_SECRET"),
        "code": code,
        "redirect_uri": os.getenv("AVITO_REDIRECT_URI")
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            response.raise_for_status()
            token_data = await response.json()
            if "access_token" not in token_data or "expires_in" not in token_data:
                raise ValueError("Неправильный формат ответа сервера Avito")
            return token_data

async def refresh_avito_token(refresh_token: str) -> dict:
    if not refresh_token:
        raise ValueError("Refresh token is required")
    
    url = "https://api.avito.ru/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    headers = {
        "Authorization": f"Bearer {AVITO_CLIENT_SECRET}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                response.raise_for_status()
                token_data = await response.json()
                if "access_token" not in token_data or "expires_in" not in token_data:
                    raise ValueError("Неправильный формат ответа сервера Avito")
                return token_data
    except aiohttp.ClientResponseError as e:
        logger.error(f"Ошибка обновления токена: {e.status} - {await response.text()}")
        raise

async def get_client_credentials_token(client_id: str, client_secret: str) -> dict:
    url = "https://api.avito.ru/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            response.raise_for_status()
            token_data = await response.json()
            token_data['expires_at'] = datetime.now() + timedelta(seconds=token_data['expires_in'])
            return token_data

async def check_token_validity(access_token: str) -> bool:
    try:
        api = AvitoAPI(access_token)
        await api._get_user_id()  # Используем внутренний метод получения user_id
        return True
    except AvitoAPIError as e:
        logger.error(f"Token check failed: {str(e)}")
        return False

async def save_avito_account(
    session: AsyncSession,
    manager_id: int,
    access_token: str,
    refresh_token: str,
    expires_in: int,
    account_name: str = "Основной аккаунт"
):
    try:
        new_account = AvitoAccount(
            account_name=account_name,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            manager_id=manager_id
        )
        
        session.add(new_account)
        await session.commit()
        await session.refresh(new_account)
        return new_account
    
    except Exception as e:
        await session.rollback()
        raise e