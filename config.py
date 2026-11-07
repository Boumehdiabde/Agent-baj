"""Configuration management for Agent OS."""
import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    FASTAPI_ENV: str = "development"
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    FASTAPI_RELOAD: bool = True

    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/agent_baj"
    SQLALCHEMY_ECHO: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    SECRET_KEY: str = "change-me-in-production"
    API_KEY: Optional[str] = None
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    LOG_LEVEL: str = "INFO"
    MAX_ITERATIONS: int = 10
    TIMEOUT: int = 300

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured browser origins, excluding empty entries."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
