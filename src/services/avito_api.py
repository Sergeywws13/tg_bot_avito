import aiohttp
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class AvitoAPIError(Exception):
    pass

class AvitoAPI:
    def __init__(self, access_token: str):
        self.base_url = "https://api.avito.ru"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    if response.status != 200:
                        error = await response.text()
                        raise AvitoAPIError(f"API Error {response.status}: {error}")
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Connection error: {str(e)}")
            raise AvitoAPIError("Connection failed") from e

    async def _get_user_id(self) -> int:
        """Получаем user_id из API"""
        endpoint = "/core/v1/accounts/self"
        data = await self._request("GET", endpoint)
        return data['id']

    async def get_unread_chats(self):
        """Получить чаты с непрочитанными сообщениями"""
        user_id = await self._get_user_id()
        endpoint = f"/messenger/v2/accounts/{user_id}/chats?unread_only=true"
        return await self._request("GET", endpoint)

    async def get_unread_messages(self, chat_id: str):
        """Получить непрочитанные сообщения"""
        user_id = await self._get_user_id()
        endpoint = f"/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages"
        return await self._request("GET", endpoint)

    async def send_message(self, chat_id: str, text: str) -> Dict:
        """Отправить текстовое сообщение"""
        user_id = await self._get_user_id()
        endpoint = f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages"
        data = {
            "message": {"text": text},
            "type": "text"
        }
        return await self._request("POST", endpoint, json=data)