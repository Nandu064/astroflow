from sqlalchemy import String, Float, Boolean, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.database import Base


class Asteroid(Base):
    __tablename__ = "asteroids"
    __table_args__ = (Index("ix_asteroid_approach_date", "approach_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    nasa_id: Mapped[str | None] = mapped_column(String(60), unique=True, nullable=True)
    dist_au: Mapped[float] = mapped_column(Float, default=0.0)
    vel_km_s: Mapped[float] = mapped_column(Float, default=0.0)
    diam_min_m: Mapped[float] = mapped_column(Float, default=0.0)
    diam_max_m: Mapped[float] = mapped_column(Float, default=0.0)
    hazardous: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    approach_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
