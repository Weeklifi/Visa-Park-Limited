import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env" if os.getenv("APP_ENV") != "docker" else None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/visapark"
    redis_url: str = "redis://localhost:6379/0"

    jwt_private_key: str = "CHANGE_ME_DEV_ONLY_PRIVATE_KEY"
    jwt_public_key: str = "CHANGE_ME_DEV_ONLY_PUBLIC_KEY"
    jwt_algorithm: str = "HS256"  # switch to RS256 in production with real key pair
    access_token_expire_minutes: int = 15

    max_total_users: int = 11111
    max_layer: int = 4
    max_children_per_node: int = 10
    vendor_markup_multiplier: str = "1.80"

    rate_limit_per_minute: int = 100


settings = Settings()
