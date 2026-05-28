"""WebSocket connection manager and real-time broadcast loop."""
import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Set

import psutil
from fastapi import WebSocket
from sqlalchemy import select, asc

from app.database import AsyncSessionLocal
from app.models.asteroid import Asteroid
from app.models.etl_job import ETLJob

log = logging.getLogger(__name__)

_clients: Set[WebSocket] = set()
_start_time = time.time()
_broadcast_task: asyncio.Task | None = None
_cache_task: asyncio.Task | None = None

# DB-sourced data cached separately so the broadcast loop never touches the DB
_cached_neo: dict | None = None
_cached_etl: list = []
_cache_last_updated: float = 0.0


def connected_count() -> int:
    return len(_clients)


async def connect(ws: WebSocket) -> None:
    await ws.accept()
    _clients.add(ws)
    log.info("WS client connected — total: %d", len(_clients))


async def disconnect(ws: WebSocket) -> None:
    _clients.discard(ws)
    log.info("WS client disconnected — total: %d", len(_clients))


async def _refresh_cache() -> None:
    """Refresh DB-sourced cache every 5 seconds."""
    global _cached_neo, _cached_etl, _cache_last_updated
    try:
        async with AsyncSessionLocal() as db:
            nearest = (
                await db.execute(
                    select(Asteroid).order_by(asc(Asteroid.dist_au)).limit(1)
                )
            ).scalar_one_or_none()

            etl_rows = (await db.execute(select(ETLJob))).scalars().all()

        _cached_neo = {
            "name": nearest.name,
            "dist_au": nearest.dist_au,
            "vel_km_s": nearest.vel_km_s,
            "diam_min_m": nearest.diam_min_m,
            "diam_max_m": nearest.diam_max_m,
            "hazardous": nearest.hazardous,
        } if nearest else None

        _cached_etl = [
            {
                "name": j.job_name,
                "status": j.status,
                "last_run_at": j.last_run_at.isoformat() if j.last_run_at else None,
                "duration_s": j.duration_s,
                "records": j.records_processed,
                "success_rate": j.success_rate,
                "error": j.error_msg,
            }
            for j in etl_rows
        ]
        _cache_last_updated = time.time()
    except Exception as exc:
        log.warning("Cache refresh failed: %s", exc)


async def _cache_loop() -> None:
    """Refresh DB cache every 5 seconds."""
    while True:
        await _refresh_cache()
        await asyncio.sleep(5)


def _build_payload() -> dict:
    """Build broadcast payload from cache + live psutil — no DB calls."""
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "cpu": round(cpu, 1),
            "mem": round(mem.percent, 1),
            "mem_used_gb": round(mem.used / 1024**3, 2),
            "connections": len(_clients),
            "uptime_s": round(time.time() - _start_time, 0),
        },
        "neo": _cached_neo,
        "etl": _cached_etl,
    }


async def _broadcast_loop() -> None:
    while True:
        await asyncio.sleep(1)
        if not _clients:
            continue
        try:
            payload = _build_payload()
            msg = json.dumps(payload, default=str)
            dead: Set[WebSocket] = set()
            for ws in list(_clients):
                try:
                    await ws.send_text(msg)
                except Exception as send_exc:
                    log.warning("WS send failed, dropping client: %s", send_exc)
                    dead.add(ws)
            _clients.difference_update(dead)
        except Exception as exc:
            log.exception("Broadcast loop error: %s", exc)


async def start_broadcast() -> None:
    global _broadcast_task, _cache_task
    _cache_task = asyncio.create_task(_cache_loop())
    _broadcast_task = asyncio.create_task(_broadcast_loop())
    log.info("WebSocket broadcast loop started")


async def stop_broadcast() -> None:
    for task in (_broadcast_task, _cache_task):
        if task:
            task.cancel()
