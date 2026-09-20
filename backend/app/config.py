from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict



PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "Lenny Growth Assistant"
    APP_ENV: str = "development"
    PORT: int = 8000

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:password123@localhost:5432/lenny_assistant"
    )

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"

    DEFAULT_PROVIDER: str = "ollama"

    CLOUD_API_KEY: str = ""
    CLOUD_MODEL: str = ""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()