import os
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)

class Settings:
    def __init__(self):
        self.BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
        self.ADMIN_IDS: List[int] = self._parse_admin_ids(os.getenv("ADMIN_IDS", "[]"))
        self.DB_URL: str = os.getenv("DB_URL", "postgresql+asyncpg://postgres:asd228asd@localhost:5432/bobcat64_miniapp")
        self.BASE_SITE: str = os.getenv("BASE_SITE", "")
        self.CHAT_ID: str = os.getenv("CHAT_ID", "")

    def _parse_admin_ids(self, admin_ids: str) -> List[int]:
        """Парсит строку с ID администраторов в список целых чисел."""
        try:
            return eval(admin_ids)  # Используем eval, чтобы распарсить строку как список
        except (SyntaxError, ValueError):
            return []

    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.BASE_SITE}/webhook"


# Получаем параметры для загрузки переменных среды
settings = Settings()
database_url = settings.DB_URL