from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator, Optional
import redis.asyncio as aioredis

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
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

    # Import all models so Base knows about them before create_all
    from app.models import asteroid, solar_event, exoplanet, etl_job  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
