from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/astroflow"
    redis_url: str = "redis://localhost:6379/0"

    nasa_api_key: str = "DEMO_KEY"

    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    neo_fetch_interval_hours: int = 6
    space_weather_fetch_interval_minutes: int = 30
    solar_flares_fetch_interval_minutes: int = 30
    exoplanets_fetch_interval_hours: int = 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def parse_env_var(cls, field_name: str, raw_val: str):
        if field_name == "cors_origins":
            try:
                return json.loads(raw_val)
            except Exception:
                return [s.strip() for s in raw_val.split(",")]
        return cls.model_validators.get(field_name, lambda v: v)(raw_val)


settings = Settings()
