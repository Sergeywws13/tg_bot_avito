import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
POSTGRES_URL = os.getenv("POSTGRES_URL")
POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB=os.getenv("POSTGRES_DB")
PGADMIN_EMAIL=os.getenv("PGADMIN_EMAIL")
PGADMIN_PASSWORD=os.getenv("PGADMIN_PASSWORD")

ENCRYPTION_KEY=os.getenv("ENCRYPTION_KEY")
AVITO_API_URL = "https://api.avito.ru/"


AVITO_CLIENT_ID=os.getenv("AVITO_CLIENT_ID")
AVITO_CLIENT_SECRET=os.getenv("AVITO_CLIENT_SECRET")
AVITO_REDIRECT_URI=os.getenv("AVITO_REDIRECT_URI")

