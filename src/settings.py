from typing import Literal

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="forbid",
    )

    ENVIRONMENT: Literal["development", "production"]
    SECRET_KEY: str
    DATABASE_URL: AnyUrl


settings = Settings()  # pyright: ignore[reportCallIssue]
