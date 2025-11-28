from functools import lru_cache
from os import getenv

from dotenv import load_dotenv
from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()

class Settings(BaseSettings):

    model_config = SettingsConfigDict(extra="ignore")

    database_url: str | None = getenv("DATABASE_URL")
    database_host: str = getenv("DATABASE_HOST")
    database_port: int = getenv("DATABASE_PORT")
    database_user: str = getenv("DATABASE_USER")
    database_password: SecretStr = SecretStr(getenv("DATABASE_PASSWORD"))
    database_db: str = getenv("DATABASE_DB")

    YACLoud_FOLDER_ID: str = getenv("YANDEX_FOLDER_ID")
    YACLoud_API_KEY: str = getenv("YANDEX_API_KEY")
    QWEN_MODEL: str = f"gpt://{YACLoud_FOLDER_ID}/qwen3-235b-a22b-fp8/latest"
    QWEN_TEMPERATURE: float = 0.1
    QWEN_MAX_TOKENS: int = 1500

    def build_database_url(self) -> str | PostgresDsn:
        if self.database_url:
            return self.database_url
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.database_user,
            password=self.database_password.get_secret_value(),
            host=self.database_host,
            port=self.database_port,
            path=f"/{self.database_db}",
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
