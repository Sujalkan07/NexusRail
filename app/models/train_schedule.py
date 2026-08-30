from datetime import date

from sqlalchemy import Boolean, Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TrainSchedule(Base):
    __tablename__ = "train_schedule"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_system: Mapped[str] = mapped_column(String(50), default="COA")
    railway_zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    division: Mapped[str | None] = mapped_column(String(100), nullable=True)
    section_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    route_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    train_no: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    service_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    origin_station: Mapped[str | None] = mapped_column(String(100), nullable=True)
    destination_station: Mapped[str | None] = mapped_column(String(100), nullable=True)
    direction: Mapped[str | None] = mapped_column(String(20), nullable=True)
    arrival_time: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    departure_time: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_goods: Mapped[bool | None] = mapped_column(Boolean, default=False)
    status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    last_updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
