"""ETL: NASA NeoWs — Near Earth Object feed."""
import time
import logging
from datetime import datetime, timedelta, timezone

import aiohttp
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.asteroid import Asteroid
from app.etl.base import mark_running, mark_done, mark_failed, mark_rate_limited

log = logging.getLogger(__name__)
JOB = "NASA NEO Feed"
URL = "https://api.nasa.gov/neo/rest/v1/feed"


async def run() -> None:
    t0 = time.time()
    await mark_running(JOB)
    try:
        today = datetime.now(timezone.utc).date()
        end = today + timedelta(days=7)
        params = {
            "start_date": today.isoformat(),
            "end_date": end.isoformat(),
            "api_key": settings.nasa_api_key,
        }

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(URL, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()

        count = 0
        async with AsyncSessionLocal() as db:
            for _date, neos in data.get("near_earth_objects", {}).items():
                for neo in neos:
                    nasa_id = neo.get("id")
                    ca = (neo.get("close_approach_data") or [{}])[0]
                    diam = neo.get("estimated_diameter", {}).get("meters", {})

                    approach_date = None
                    raw_date = ca.get("close_approach_date_full") or ca.get("close_approach_date")
                    if raw_date:
                        try:
                            approach_date = datetime.strptime(raw_date[:10], "%Y-%m-%d")
                        except ValueError:
                            pass

                    dist_au = float(ca.get("miss_distance", {}).get("astronomical", 0) or 0)
                    vel = float(ca.get("relative_velocity", {}).get("kilometers_per_second", 0) or 0)
                    diam_min = float(diam.get("estimated_diameter_min", 0) or 0)
                    diam_max = float(diam.get("estimated_diameter_max", 0) or 0)
                    hazardous = bool(neo.get("is_potentially_hazardous_asteroid", False))

                    existing = (
                        await db.execute(select(Asteroid).where(Asteroid.nasa_id == nasa_id))
                    ).scalar_one_or_none()

                    if existing:
                        existing.dist_au = dist_au
                        existing.vel_km_s = vel
                        existing.diam_min_m = diam_min
                        existing.diam_max_m = diam_max
                        existing.hazardous = hazardous
                        existing.approach_date = approach_date
                        existing.updated_at = datetime.now(timezone.utc)
                    else:
                        db.add(Asteroid(
                            name=neo.get("name", "Unknown"),
                            nasa_id=nasa_id,
                            dist_au=dist_au,
                            vel_km_s=vel,
                            diam_min_m=diam_min,
                            diam_max_m=diam_max,
                            hazardous=hazardous,
                            approach_date=approach_date,
                        ))
                    count += 1

            await db.commit()

        await mark_done(JOB, count, time.time() - t0)

    except aiohttp.ClientResponseError as exc:
        if exc.status == 429:
            await mark_rate_limited(JOB, time.time() - t0)
        else:
            await mark_failed(JOB, str(exc), time.time() - t0)
            log.exception("NASA NEO ETL error")
    except Exception as exc:
        await mark_failed(JOB, str(exc), time.time() - t0)
        log.exception("NASA NEO ETL error")
