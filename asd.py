from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Проверяем, что ENCRYPTION_KEY загружен
encryption_key = os.getenv("ENCRYPTION_KEY")
if not encryption_key:
    raise ValueError("ENCRYPTION_KEY не найден в переменных окружения.")

print(f"ENCRYPTION_KEY: {encryption_key}")