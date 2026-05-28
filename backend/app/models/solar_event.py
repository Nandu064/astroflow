from sqlalchemy import String, Float, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.database import Base


class SolarEvent(Base):
    __tablename__ = "solar_events"
    __table_args__ = (Index("ix_solar_event_start_time", "start_time"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    nasa_id: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    class_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    kp_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    peak_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_location: Mapped[str | None] = mapped_column(String(60), nullable=True)
    instruments: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
