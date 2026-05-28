from typing import Optional, List
from datetime import datetime
import strawberry


@strawberry.type
class AsteroidType:
    id: int
    name: str
    nasa_id: Optional[str]
    dist_au: float
    vel_km_s: float
    diam_min_m: float
    diam_max_m: float
    hazardous: bool
    approach_date: Optional[datetime]
    created_at: datetime


@strawberry.type
class SolarEventType:
    id: int
    event_type: str
    nasa_id: Optional[str]
    class_type: Optional[str]
    kp_index: Optional[float]
    start_time: Optional[datetime]
    peak_time: Optional[datetime]
    end_time: Optional[datetime]
    source_location: Optional[str]
    instruments: Optional[str]
    created_at: datetime


@strawberry.type
class ExoplanetType:
    id: int
    name: str
    host_star: Optional[str]
    dist_ly: Optional[float]
    radius_earth: Optional[float]
    mass_earth: Optional[float]
    orbital_period_days: Optional[float]
    discovery_year: Optional[int]
    discovery_method: Optional[str]
    equilibrium_temp_k: Optional[float]
    created_at: datetime


@strawberry.type
class ETLJobType:
    id: int
    job_name: str
    status: str
    last_run_at: Optional[datetime]
    duration_s: Optional[float]
    records_processed: int
    total_records: int
    error_msg: Optional[str]
    success_rate: float
    next_run_at: Optional[datetime]


@strawberry.type
class ServerHealthType:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    uptime_seconds: float
    active_ws_connections: int
    db_status: str
    redis_status: str
    api_latency_ms: float
    status: str


@strawberry.type
class PaginatedAsteroids:
    items: List[AsteroidType]
    total: int
    page: int
    per_page: int
    total_pages: int


@strawberry.type
class PaginatedExoplanets:
    items: List[ExoplanetType]
    total: int
    page: int
    per_page: int
    total_pages: int


@strawberry.type
class DashboardSummaryType:
    neo_count: int
    hazardous_count: int
    solar_event_count: int
    exoplanet_count: int
    etl_jobs_running: int
    etl_jobs_healthy: int
