"""Shared helpers for all ETL workers."""
import time
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.etl_job import ETLJob

log = logging.getLogger(__name__)


async def get_or_create_job(db, job_name: str) -> ETLJob:
    job = (await db.execute(select(ETLJob).where(ETLJob.job_name == job_name))).scalar_one_or_none()
    if not job:
        job = ETLJob(job_name=job_name)
        db.add(job)
        await db.flush()
    return job


async def mark_running(job_name: str) -> None:
    async with AsyncSessionLocal() as db:
        job = await get_or_create_job(db, job_name)
        job.status = "running"
        job.error_msg = None
        await db.commit()


async def mark_done(job_name: str, records: int, duration: float, total: int = 0) -> None:
    async with AsyncSessionLocal() as db:
        job = await get_or_create_job(db, job_name)
        job.status = "idle"
        job.last_run_at = datetime.now(timezone.utc)
        job.duration_s = round(duration, 2)
        job.records_processed = records
        job.total_records = total or records
        job.error_msg = None
        job.success_rate = 100.0
        await db.commit()
    log.info("[ETL] %s done — %d records in %.2fs", job_name, records, duration)


async def mark_failed(job_name: str, error: str, duration: float) -> None:
    async with AsyncSessionLocal() as db:
        job = await get_or_create_job(db, job_name)
        job.status = "failed"
        job.last_run_at = datetime.now(timezone.utc)
        job.duration_s = round(duration, 2)
        job.error_msg = str(error)[:2000]
        job.success_rate = max(0.0, job.success_rate - 10.0)
        await db.commit()
    log.error("[ETL] %s failed: %s", job_name, error)


async def mark_rate_limited(job_name: str, duration: float) -> None:
    """Called on HTTP 429 — keeps job idle so success_rate is not degraded."""
    async with AsyncSessionLocal() as db:
        job = await get_or_create_job(db, job_name)
        job.status = "idle"
        job.last_run_at = datetime.now(timezone.utc)
        job.duration_s = round(duration, 2)
        job.error_msg = (
            "Rate limited by NASA API (DEMO_KEY). "
            "Get a free key at https://api.nasa.gov and set NASA_API_KEY in .env"
        )
        # success_rate intentionally NOT degraded — this is a quota issue, not a code failure
        await db.commit()
    log.warning("[ETL] %s skipped — NASA API rate limit (429). Use a real API key.", job_name)
