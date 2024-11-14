import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: List[int]
    DB_URL: str = "postgresql+asyncpg://postgres:asd228asd@localhost:5432/bobcat64_miniapp"
    BASE_SITE: str
    CHAT_ID: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.BASE_SITE}/webhook"


# Получаем параметры для загрузки переменных среды
settings = Settings()
database_url = settings.DB_URL