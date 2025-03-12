from asyncpg import create_pool
import os

async def get_db_pool():
    return await create_pool(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
        host="localhost"
    )
