"""APScheduler setup — manages all ETL cron jobs."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.etl import nasa_neo, solar_flares, noaa_weather, exoplanets

log = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def start_scheduler() -> None:
    global _scheduler

    _scheduler = AsyncIOScheduler(timezone="UTC")

    _scheduler.add_job(
        nasa_neo.run,
        trigger=IntervalTrigger(hours=settings.neo_fetch_interval_hours),
        id="nasa_neo",
        name="NASA NEO Feed",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    _scheduler.add_job(
        solar_flares.run,
        trigger=IntervalTrigger(minutes=settings.solar_flares_fetch_interval_minutes),
        id="solar_flares",
        name="Solar Flare Events",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    _scheduler.add_job(
        noaa_weather.run,
        trigger=IntervalTrigger(minutes=settings.space_weather_fetch_interval_minutes),
        id="noaa_weather",
        name="NOAA Space Weather",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    _scheduler.add_job(
        exoplanets.run,
        trigger=IntervalTrigger(hours=settings.exoplanets_fetch_interval_hours),
        id="exoplanets",
        name="Exoplanet Archive",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    _scheduler.start()
    log.info("ETL scheduler started with %d jobs", len(_scheduler.get_jobs()))

    # Run each job once immediately on startup (non-blocking)
    import asyncio
    for job_fn in (nasa_neo.run, solar_flares.run, noaa_weather.run, exoplanets.run):
        asyncio.create_task(job_fn())


async def stop_scheduler() -> None:
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        log.info("ETL scheduler stopped")


def get_scheduler() -> AsyncIOScheduler | None:
    return _scheduler
