from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator, Optional
import redis.asyncio as aioredis

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


_redis_client: Optional[aioredis.Redis] = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_redis() -> Optional[aioredis.Redis]:
    return _redis_client


async def init_db() -> None:
    global _redis_client
    import asyncio
    import logging
    log = logging.getLogger(__name__)

    # Import all models so Base knows about them before create_all
    from app.models import asteroid, solar_event, exoplanet, etl_job  # noqa: F401

    # Retry DB connection — Railway Postgres can take a few seconds to be ready
    for attempt in range(1, 11):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            log.info("Database ready after %d attempt(s)", attempt)
            break
        except Exception as exc:
            if attempt == 10:
                log.error("Database unavailable after 10 attempts — giving up: %s", exc)
                raise
            log.warning("DB not ready (attempt %d/10): %s — retrying in 3s", attempt, exc)
            await asyncio.sleep(3)

    # Redis is optional — app works without it
    try:
        _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await _redis_client.ping()
        log.info("Redis connected")
    except Exception as exc:
        log.warning("Redis unavailable — continuing without it: %s", exc)
        _redis_client = None
