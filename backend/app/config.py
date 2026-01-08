from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "News Aggregator"
    debug: bool = False

    # Переменная окружения DATABASE_URL в docker-compose будет источником истины
    database_url: str = "postgresql+asyncpg://news:news@db:5432/news"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

