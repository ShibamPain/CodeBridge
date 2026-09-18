"""
Loads environment variables from .env into a typed Settings object.
Import `settings` anywhere you need config instead of calling os.getenv directly.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PORT: int = 8000
    ENV: str = "development"
    API_KEY: str = "changeme"
    CORS_ORIGINS: str = "*"
    CONFIDENCE_THRESHOLD: float = 0.85

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()