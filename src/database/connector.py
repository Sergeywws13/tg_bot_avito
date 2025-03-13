from asyncpg import create_pool
import os

class Database:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        self.pool = await create_pool(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB"),
            host="localhost",
            port=5433,
            min_size=5,
            max_size=20
        )

    async def get_pool(self):
        if not self.pool:
            await self.create_pool()
        return self.pool

db = Database()