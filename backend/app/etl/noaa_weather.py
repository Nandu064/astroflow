"""ETL: NOAA Space Weather — Geomagnetic storm & Kp index data."""
import time
import logging
from datetime import datetime

import aiohttp

from app.database import AsyncSessionLocal
from app.models.solar_event import SolarEvent
from app.etl.base import mark_running, mark_done, mark_failed

log = logging.getLogger(__name__)
JOB = "NOAA Space Weather"
KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
STORM_URL = "https://services.swpc.noaa.gov/products/noaa-alerts.json"


async def run() -> None:
    t0 = time.time()
    await mark_running(JOB)
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
            async with session.get(KP_URL) as resp:
                resp.raise_for_status()
                kp_data = await resp.json()

        count = 0
        async with AsyncSessionLocal() as db:
            # kp_data[0] is header row; rest are [timestamp, kp, ...]
            for row in (kp_data[1:] if len(kp_data) > 1 else []):
                try:
                    ts_str = row[0] if isinstance(row, list) else None
                    kp_val = float(row[1]) if isinstance(row, list) and len(row) > 1 else None
                    if not ts_str or kp_val is None:
                        continue
                    ts = datetime.strptime(ts_str[:16], "%Y-%m-%d %H:%M")
                    nasa_id = f"NOAA-KP-{ts_str[:16].replace(' ', 'T')}"

                    from sqlalchemy import select
                    existing = (
                        await db.execute(
                            select(SolarEvent).where(SolarEvent.nasa_id == nasa_id)
                        )
                    ).scalar_one_or_none()
                    if existing:
                        existing.kp_index = kp_val
                    else:
                        db.add(SolarEvent(
                            event_type="KP_INDEX",
                            nasa_id=nasa_id,
                            kp_index=kp_val,
                            start_time=ts,
                        ))
                    count += 1
                except Exception:
                    continue

            await db.commit()

        await mark_done(JOB, count, time.time() - t0)

    except Exception as exc:
        await mark_failed(JOB, str(exc), time.time() - t0)
        log.exception("NOAA Space Weather ETL error")
