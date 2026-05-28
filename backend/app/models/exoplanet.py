from sqlalchemy import String, Float, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.database import Base


class Exoplanet(Base):
    __tablename__ = "exoplanets"
    __table_args__ = (Index("ix_exoplanet_discovery_year", "discovery_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    host_star: Mapped[str | None] = mapped_column(String(150), nullable=True)
    dist_ly: Mapped[float | None] = mapped_column(Float, nullable=True)
    radius_earth: Mapped[float | None] = mapped_column(Float, nullable=True)
    mass_earth: Mapped[float | None] = mapped_column(Float, nullable=True)
    orbital_period_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    discovery_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discovery_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    equilibrium_temp_k: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
