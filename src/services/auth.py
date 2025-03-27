from datetime import datetime, timedelta
import aiohttp
import os
import logging

from src.database.connector import db
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
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response_text = await response.text()
                logger.info(f"Response from token endpoint: {response_text}")
                response.raise_for_status()
                token_data = await response.json()
                if "access_token" not in token_data or "expires_in" not in token_data:
                    raise ValueError("Неправильный формат ответа сервера Avito")
                print(token_data)
                return token_data
    except aiohttp.ClientResponseError as e:
        logger.error(f"Ошибка получения токена: {e.status} - {await response.text()}")
        raise


async def refresh_avito_token(refresh_token: str, account_id: int) -> dict:
    if not refresh_token:
        raise ValueError("Refresh token is required")
    
    url = "https://api.avito.ru/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": os.getenv("AVITO_CLIENT_ID"),
        "client_secret": os.getenv("AVITO_CLIENT_SECRET")
    }
    
    try:
        logger.info(f"Refreshing token for account_id: {account_id}")
        logger.info(f"Refresh token: {refresh_token}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response_text = await response.text()
                logger.info(f"Response from Avito API: {response_text}")
                response.raise_for_status()
                token_data = await response.json()
                
                if "access_token" not in token_data or "expires_in" not in token_data:
                    raise ValueError("Неправильный формат ответа сервера Avito")
                
                # Обновляем запись в базе данных
                async with db.session_factory() as db_session:
                    account = await db_session.get(AvitoAccount, account_id)
                    if not account:
                        raise ValueError(f"Account with id {account_id} not found")
                    
                    account.access_token = token_data["access_token"]
                    account.refresh_token = token_data.get("refresh_token", refresh_token)  # Если новый refresh_token не возвращается
                    account.expires_at = datetime.now() + timedelta(seconds=token_data["expires_in"])
                    await db_session.commit()
                
                logger.info(f"Token refreshed for account_id: {account_id}")
                return token_data
    except aiohttp.ClientResponseError as e:
        logger.error(f"Ошибка обновления токена: {e.status} - {await response.text()}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in refresh_avito_token: {str(e)}")
        raise


async def check_token_validity(access_token: str) -> bool:
    try:
        api = AvitoAPI(access_token)
        await api._get_user_id()
        return True
    except AvitoAPIError as e:
        logger.error(f"Token check failed: {str(e)}")
        return False
