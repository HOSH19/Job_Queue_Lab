from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+psycopg://jobqueue:jobqueue@localhost:5432/jobqueue"
    queue_key: str = "jobqueue:jobs"
    delayed_key: str = "jobqueue:delayed"
    dlq_key: str = "jobqueue:dlq"
    events_channel: str = "jobqueue:events"
    max_attempts: int = 3
    cors_origins: str = "http://localhost:5173"
    api_key: str = ""
    rate_limit: str = "60/minute"
    log_json: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def auth_enabled(self) -> bool:
        return bool(self.api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
