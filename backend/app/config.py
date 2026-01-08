from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    debug: bool = False

    database_url: str = "postgresql+asyncpg://news:news@db:5432/news"

    fetch_interval_seconds: int = 300  # 5 минут
    fetch_max_items_per_feed: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
