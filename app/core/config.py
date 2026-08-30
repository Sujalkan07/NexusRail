import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NexusRail"
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL") or "postgresql+psycopg://postgres:postgres@localhost:5432/nexusrail"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
