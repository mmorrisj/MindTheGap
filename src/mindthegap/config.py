from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MTG_", env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./mindthegap.db"
    github_token: str | None = None
    http_timeout: float = 15.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
