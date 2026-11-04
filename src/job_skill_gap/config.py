import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://redis:6379/0"
    import_interval_minutes: int = 60
    import_pause: float = 1.0
    companies_dir: Path = Path("data/companies")


@lru_cache
def get_settings() -> Settings:
    return Settings()
