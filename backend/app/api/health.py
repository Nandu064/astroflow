"""REST health endpoints — /health and /health/etl."""
import time
import psutil
from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import select, func

from app.database import AsyncSessionLocal, get_redis
from app.models.etl_job import ETLJob
from app.services.broadcaster import connected_count

router = APIRouter(tags=["health"])

_start = time.time()
_last_cpu: float = 0.0   # cache last non-zero reading; psutil returns 0 on first call

# Prime the cpu_percent baseline immediately so first real call returns a value
psutil.cpu_percent(interval=None)


@router.get("")
async def server_health():
    global _last_cpu
    cpu = psutil.cpu_percent(interval=None)   # non-blocking; uses baseline set above
    if cpu > 0:
        _last_cpu = cpu
    else:
        cpu = _last_cpu   # return last known value instead of 0
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    db_ok = True
    db_latency_ms = 0.0
    try:
        t0 = time.perf_counter()
        async with AsyncSessionLocal() as db:
            await db.execute(select(func.now()))
        db_latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    except Exception:
        db_ok = False

    redis_ok = False
    redis_latency_ms = 0.0
    redis = get_redis()
    if redis:
        try:
            t0 = time.perf_counter()
            await redis.ping()
            redis_latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            redis_ok = True
        except Exception:
            pass

    uptime = round(time.time() - _start, 1)
    status = "ok" if db_ok else "degraded"

    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime,
        "cpu_percent": round(cpu, 1),
        "memory": {
            "percent": round(mem.percent, 1),
            "used_gb": round(mem.used / 1024**3, 2),
            "total_gb": round(mem.total / 1024**3, 2),
        },
        "disk": {
            "percent": round(disk.percent, 1),
            "free_gb": round(disk.free / 1024**3, 2),
        },
        "database": {"ok": db_ok, "latency_ms": db_latency_ms},
        "redis": {"ok": redis_ok, "latency_ms": redis_latency_ms},
        "websocket_connections": connected_count(),
    }


@router.get("/etl")
async def etl_health():
    async with AsyncSessionLocal() as db:
        jobs = (await db.execute(select(ETLJob).order_by(ETLJob.job_name))).scalars().all()

    job_list = []
    for j in jobs:
        last_run_ago_s = None
        if j.last_run_at:
            last_run_ago_s = round((datetime.now(timezone.utc) - j.last_run_at).total_seconds())

        job_list.append({
            "name": j.job_name,
            "status": j.status,
            "last_run_at": j.last_run_at.isoformat() if j.last_run_at else None,
            "last_run_ago_s": last_run_ago_s,
            "duration_s": j.duration_s,
            "records_processed": j.records_processed,
            "success_rate": j.success_rate,
            "error": j.error_msg,
            "next_run_at": j.next_run_at.isoformat() if j.next_run_at else None,
            "healthy": j.status != "failed",
        })

    total = len(job_list)
    healthy = sum(1 for j in job_list if j["healthy"])
    running = sum(1 for j in job_list if j["status"] == "running")

    return {
        "status": "ok" if healthy == total else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {"total": total, "healthy": healthy, "running": running, "failed": total - healthy},
        "jobs": job_list,
    }
