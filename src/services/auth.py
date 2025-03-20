import aiohttp
import os
import logging

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
                return token_data
    except aiohttp.ClientResponseError as e:
        logger.error(f"Ошибка получения токена: {e.status} - {await response.text()}")
        raise


async def refresh_avito_token(refresh_token: str) -> dict:
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
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response.raise_for_status()
                token_data = await response.json()
                if "access_token" not in token_data or "expires_in" not in token_data:
                    raise ValueError("Неправильный формат ответа сервера Avito")
                return token_data
    except aiohttp.ClientResponseError as e:
        logger.error(f"Ошибка обновления токена: {e.status} - {await response.text()}")
        raise
    print(token_data)


async def check_token_validity(access_token: str) -> bool:
    try:
        api = AvitoAPI(access_token)
        await api._get_user_id()
        return True
    except AvitoAPIError as e:
        logger.error(f"Token check failed: {str(e)}")
        return False
