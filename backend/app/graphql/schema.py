from typing import Optional, List
from datetime import datetime
import time
import strawberry
import psutil

from sqlalchemy import select, func, desc, asc
from app.database import AsyncSessionLocal, get_redis
from app.models.asteroid import Asteroid
from app.models.solar_event import SolarEvent
from app.models.exoplanet import Exoplanet
from app.models.etl_job import ETLJob
from app.graphql.types import (
    AsteroidType, SolarEventType, ExoplanetType, ETLJobType,
    ServerHealthType, PaginatedAsteroids, PaginatedExoplanets,
    DashboardSummaryType,
)

_start_time = time.time()


# ── Mappers ─────────────────────────────────────────────────────────────────

def _asteroid(a: Asteroid) -> AsteroidType:
    return AsteroidType(
        id=a.id, name=a.name, nasa_id=a.nasa_id,
        dist_au=a.dist_au, vel_km_s=a.vel_km_s,
        diam_min_m=a.diam_min_m, diam_max_m=a.diam_max_m,
        hazardous=a.hazardous, approach_date=a.approach_date,
        created_at=a.created_at,
    )


def _solar(e: SolarEvent) -> SolarEventType:
    return SolarEventType(
        id=e.id, event_type=e.event_type, nasa_id=e.nasa_id,
        class_type=e.class_type, kp_index=e.kp_index,
        start_time=e.start_time, peak_time=e.peak_time,
        end_time=e.end_time, source_location=e.source_location,
        instruments=e.instruments, created_at=e.created_at,
    )


def _exoplanet(p: Exoplanet) -> ExoplanetType:
    return ExoplanetType(
        id=p.id, name=p.name, host_star=p.host_star,
        dist_ly=p.dist_ly, radius_earth=p.radius_earth,
        mass_earth=p.mass_earth, orbital_period_days=p.orbital_period_days,
        discovery_year=p.discovery_year, discovery_method=p.discovery_method,
        equilibrium_temp_k=p.equilibrium_temp_k, created_at=p.created_at,
    )


def _etl_job(j: ETLJob) -> ETLJobType:
    return ETLJobType(
        id=j.id, job_name=j.job_name, status=j.status,
        last_run_at=j.last_run_at, duration_s=j.duration_s,
        records_processed=j.records_processed, total_records=j.total_records,
        error_msg=j.error_msg, success_rate=j.success_rate,
        next_run_at=j.next_run_at,
    )


# ── Query ────────────────────────────────────────────────────────────────────

@strawberry.type
class Query:

    @strawberry.field
    async def asteroids(
        self,
        hazardous_only: bool = False,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "approach_date",
        sort_desc: bool = True,
    ) -> PaginatedAsteroids:
        per_page = min(per_page, 100)
        async with AsyncSessionLocal() as db:
            base_q = select(Asteroid)
            if hazardous_only:
                base_q = base_q.where(Asteroid.hazardous.is_(True))

            total = (await db.execute(
                select(func.count()).select_from(base_q.subquery())
            )).scalar_one()

            col = getattr(Asteroid, sort_by, Asteroid.approach_date)
            order = desc(col) if sort_desc else asc(col)
            rows = (await db.execute(
                base_q.order_by(order).offset((page - 1) * per_page).limit(per_page)
            )).scalars().all()

        total_pages = max(1, (total + per_page - 1) // per_page)
        return PaginatedAsteroids(
            items=[_asteroid(a) for a in rows],
            total=total, page=page, per_page=per_page, total_pages=total_pages,
        )

    @strawberry.field
    async def asteroid(self, id: int) -> Optional[AsteroidType]:
        async with AsyncSessionLocal() as db:
            a = await db.get(Asteroid, id)
        return _asteroid(a) if a else None

    @strawberry.field
    async def solar_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[SolarEventType]:
        limit = min(limit, 500)
        async with AsyncSessionLocal() as db:
            q = select(SolarEvent).order_by(desc(SolarEvent.start_time)).limit(limit)
            if event_type:
                q = q.where(SolarEvent.event_type == event_type)
            rows = (await db.execute(q)).scalars().all()
        return [_solar(e) for e in rows]

    @strawberry.field
    async def exoplanets(
        self,
        discovery_method: Optional[str] = None,
        min_year: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedExoplanets:
        per_page = min(per_page, 100)
        async with AsyncSessionLocal() as db:
            base_q = select(Exoplanet)
            if discovery_method:
                base_q = base_q.where(Exoplanet.discovery_method == discovery_method)
            if min_year:
                base_q = base_q.where(Exoplanet.discovery_year >= min_year)

            total = (await db.execute(
                select(func.count()).select_from(base_q.subquery())
            )).scalar_one()

            rows = (await db.execute(
                base_q.order_by(desc(Exoplanet.discovery_year))
                .offset((page - 1) * per_page).limit(per_page)
            )).scalars().all()

        total_pages = max(1, (total + per_page - 1) // per_page)
        return PaginatedExoplanets(
            items=[_exoplanet(p) for p in rows],
            total=total, page=page, per_page=per_page, total_pages=total_pages,
        )

    @strawberry.field
    async def etl_jobs(self) -> List[ETLJobType]:
        async with AsyncSessionLocal() as db:
            rows = (await db.execute(select(ETLJob).order_by(ETLJob.job_name))).scalars().all()
        return [_etl_job(j) for j in rows]

    @strawberry.field
    async def dashboard_summary(self) -> DashboardSummaryType:
        async with AsyncSessionLocal() as db:
            neo_count = (await db.execute(select(func.count()).select_from(Asteroid))).scalar_one()
            hazardous = (await db.execute(
                select(func.count()).select_from(Asteroid).where(Asteroid.hazardous.is_(True))
            )).scalar_one()
            solar_count = (await db.execute(select(func.count()).select_from(SolarEvent))).scalar_one()
            exo_count = (await db.execute(select(func.count()).select_from(Exoplanet))).scalar_one()
            etl_rows = (await db.execute(select(ETLJob))).scalars().all()

        running = sum(1 for j in etl_rows if j.status == "running")
        healthy = sum(1 for j in etl_rows if j.status != "failed")
        return DashboardSummaryType(
            neo_count=neo_count, hazardous_count=hazardous,
            solar_event_count=solar_count, exoplanet_count=exo_count,
            etl_jobs_running=running, etl_jobs_healthy=healthy,
        )

    @strawberry.field
    async def server_health(self) -> ServerHealthType:
        t0 = time.perf_counter()
        cpu = psutil.cpu_percent(interval=0.05)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        uptime = time.time() - _start_time
        latency_ms = (time.perf_counter() - t0) * 1000

        db_status = "ok"
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(select(func.now()))
        except Exception:
            db_status = "error"

        redis_status = "ok"
        redis = get_redis()
        if redis:
            try:
                await redis.ping()
            except Exception:
                redis_status = "error"
        else:
            redis_status = "not_connected"

        from app.services.broadcaster import connected_count
        overall = "degraded" if db_status != "ok" or redis_status not in ("ok", "not_connected") else "ok"

        return ServerHealthType(
            cpu_percent=cpu,
            memory_percent=mem.percent,
            disk_percent=disk.percent,
            uptime_seconds=uptime,
            active_ws_connections=connected_count(),
            db_status=db_status,
            redis_status=redis_status,
            api_latency_ms=round(latency_ms, 2),
            status=overall,
        )


schema = strawberry.Schema(query=Query)
