from functools import lru_cache
from os import getenv

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings


load_dotenv()

class Settings(BaseSettings):
    database_url: str | None = getenv("DATABASE_URL")
    database_host: str = getenv("DATABASE_HOST")
    database_port: int = getenv("DATABASE_PORT")
    database_user: str = getenv("DATABASE_USER")
    database_password: SecretStr = SecretStr(getenv("DATABASE_PASSWORD"))
    database_db: str = getenv("DATABASE_DB")

    YACLoud_FOLDER_ID: str = getenv("YANDEX_FOLDER_ID", "")
    YACLoud_API_KEY: str = getenv("YANDEX_API_KEY", "")
    QWEN_TEMPERATURE: float = 0.1
    QWEN_MAX_TOKENS: int = 1500

    # Qdrant vector DB
    QDRANT_HOST: str = getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION_NAME: str = getenv("QDRANT_COLLECTION_NAME", "precedents")

    # SBERT for embeddings
    EMBEDDING_MODEL: str = getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")

    def get_qwen_model(self) -> str:
        """Возвращает полный путь к модели Qwen."""
        return f"gpt://{self.YACLoud_FOLDER_ID}/qwen3-235b-a22b-fp8/latest"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
