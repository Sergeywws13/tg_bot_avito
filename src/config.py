import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
POSTGRES_URL = os.getenv("POSTGRES_URL")
POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD=os.getenv("POSGRES_PASSWORD")
POSTGRES_DB=os.getenv("POSTGRES_DB")
PGADMIN_EMAIL=os.getenv("PGADMIN_EMAIL")
PGADMIN_PASSWORD=os.getenv("PGADMIN_PASSWORD")

ENCRYPTION_KEY=os.getenv("ENCRYPTION_KEY")
AVITO_API_URL = "https://api.avito.ru/"