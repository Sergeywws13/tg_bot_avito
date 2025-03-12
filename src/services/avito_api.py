import aiohttp
from typing import Optional, Dict, Any

class AvitoAPI:
    def __init__(self, access_token: str):
        self.base_url = "https://api.avito.ru"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    async def get_messages(self) -> Optional[Dict[str, Any]]:
        """Получить список сообщений"""
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.get(
                    f"{self.base_url}/messenger/v2/accounts/self/chats",
                    headers=self.headers
                )
                return await response.json()
            except Exception as e:
                print(f"Ошибка при получении сообщений: {e}")
                return None

    async def send_message(self, chat_id: str, text: str) -> bool:
        """Отправить ответ"""
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.post(
                    f"{self.base_url}/messenger/v2/accounts/self/chats/{chat_id}/messages",
                    headers=self.headers,
                    json={"text": text}
                )
                return response.status == 201
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")
                return False