import asyncio
from src.services.avito_api import AvitoAPI
from src.database.connector import db

async def check_new_messages():
    while True:
        pool = await db.get_pool()
        async with pool.acquire() as conn:
            accounts = await conn.fetch("SELECT * FROM avito_accounts")
            for account in accounts:
                api = AvitoAPI(account["access_token"])
                messages = await api.get_messages()
                if messages:
                    print(f"Получено {len(messages['chats'])} сообщений")
        await asyncio.sleep(300)
        
