import asyncio
from src.services.avito_api import AvitoAPI
from src.database.connector import get_db_pool



async def check_new_messages():
    while True:
        async with get_db_pool() as pool:
            async with pool.acquire() as conn:
                accounts = await conn.fetch("SELECT * FROM avito_accounts")
                for account in accounts:
                    api = AvitoAPI(account["access_token"])
                    messages = await api.get_messages()
        await asyncio.sleep(300)

asyncio.create_task(check_new_messages())
