"""ETL: NASA Exoplanet Archive — confirmed exoplanet catalog."""
import time
import csv
import io
import logging

import aiohttp
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.exoplanet import Exoplanet
from app.etl.base import mark_running, mark_done, mark_failed

log = logging.getLogger(__name__)
JOB = "Exoplanet Archive"

# TAP query — returns key columns for all confirmed planets (CSV format)
ARCHIVE_URL = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    "?query=select+pl_name,hostname,sy_dist,pl_rade,pl_bmasse,"
    "pl_orbper,disc_year,discoverymethod,pl_eqt"
    "+from+ps+where+default_flag=1"
    "&format=csv"
)


def _float(val: str) -> float | None:
    try:
        return float(val) if val.strip() else None
    except (ValueError, AttributeError):
        return None


def _int(val: str) -> int | None:
    try:
        return int(float(val)) if val.strip() else None
    except (ValueError, AttributeError):
        return None


async def run() -> None:
    t0 = time.time()
    await mark_running(JOB)
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            async with session.get(ARCHIVE_URL) as resp:
                resp.raise_for_status()
                raw = await resp.text()

        reader = csv.DictReader(io.StringIO(raw))
        rows = list(reader)

        count = 0
        async with AsyncSessionLocal() as db:
            for row in rows:
                name = (row.get("pl_name") or "").strip()
                if not name:
                    continue

                existing = (
                    await db.execute(select(Exoplanet).where(Exoplanet.name == name))
                ).scalar_one_or_none()

                # Convert distance from parsecs to light-years (1 pc = 3.26156 ly)
                dist_pc = _float(row.get("sy_dist", ""))
                dist_ly = round(dist_pc * 3.26156, 2) if dist_pc else None

                kwargs = dict(
                    host_star=(row.get("hostname") or "").strip() or None,
                    dist_ly=dist_ly,
                    radius_earth=_float(row.get("pl_rade", "")),
                    mass_earth=_float(row.get("pl_bmasse", "")),
                    orbital_period_days=_float(row.get("pl_orbper", "")),
                    discovery_year=_int(row.get("disc_year", "")),
                    discovery_method=(row.get("discoverymethod") or "").strip() or None,
                    equilibrium_temp_k=_float(row.get("pl_eqt", "")),
                )

                if existing:
                    for k, v in kwargs.items():
                        setattr(existing, k, v)
                else:
                    db.add(Exoplanet(name=name, **kwargs))
                count += 1

                # Commit in batches to avoid huge transactions
                if count % 500 == 0:
                    await db.flush()

            await db.commit()

        await mark_done(JOB, count, time.time() - t0, total=len(rows))

    except Exception as exc:
        await mark_failed(JOB, str(exc), time.time() - t0)
        log.exception("Exoplanet Archive ETL error")
