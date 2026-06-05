from pydantic_settings import BaseSettings
from pydantic import field_validator
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

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, list):
            return v
        try:
            return json.loads(v)
        except Exception:
            return [s.strip() for s in v.split(",")]

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v):
        if not isinstance(v, str):
            return v
        # Railway / Heroku / Neon provide postgresql:// — asyncpg needs postgresql+asyncpg://
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        # Neon uses ?sslmode=require — asyncpg uses ?ssl=require
        v = v.replace("sslmode=require", "ssl=require")
        return v


settings = Settings()
