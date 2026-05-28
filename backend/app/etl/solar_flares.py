"""ETL: NASA DONKI — Solar Flare events."""
import time
import logging
from datetime import datetime, timedelta, timezone

import aiohttp
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.solar_event import SolarEvent
from app.etl.base import mark_running, mark_done, mark_failed, mark_rate_limited

log = logging.getLogger(__name__)
JOB = "Solar Flare Events"
URL = "https://api.nasa.gov/DONKI/FLR"


async def run() -> None:
    t0 = time.time()
    await mark_running(JOB)
    try:
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=30)
        params = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "api_key": settings.nasa_api_key,
        }

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(URL, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()

        if not isinstance(data, list):
            data = []

        count = 0
        async with AsyncSessionLocal() as db:
            for flare in data:
                nasa_id = flare.get("flrID")
                existing = (
                    await db.execute(select(SolarEvent).where(SolarEvent.nasa_id == nasa_id))
                ).scalar_one_or_none()
                if existing:
                    continue

                def _dt(s):
                    if not s:
                        return None
                    for fmt in ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
                        try:
                            return datetime.strptime(s[:16], fmt[:len(s[:16])])
                        except ValueError:
                            continue
                    return None

                instruments = ", ".join(
                    i.get("displayName", "") for i in (flare.get("instruments") or [])
                )

                db.add(SolarEvent(
                    event_type="FLARE",
                    nasa_id=nasa_id,
                    class_type=flare.get("classType"),
                    start_time=_dt(flare.get("beginTime")),
                    peak_time=_dt(flare.get("peakTime")),
                    end_time=_dt(flare.get("endTime")),
                    source_location=flare.get("sourceLocation"),
                    instruments=instruments[:200] if instruments else None,
                ))
                count += 1

            await db.commit()

        await mark_done(JOB, count, time.time() - t0)

    except aiohttp.ClientResponseError as exc:
        if exc.status == 429:
            await mark_rate_limited(JOB, time.time() - t0)
        else:
            await mark_failed(JOB, str(exc), time.time() - t0)
            log.exception("Solar Flare ETL error")
    except Exception as exc:
        await mark_failed(JOB, str(exc), time.time() - t0)
        log.exception("Solar Flare ETL error")
