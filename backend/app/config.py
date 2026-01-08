from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "News Aggregator"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://news:news@db:5432/news"

    class Config:
        env_file = ".env"


settings = Settings()
