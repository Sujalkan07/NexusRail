from sqlalchemy import Boolean, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SmmsFailure(Base):
    __tablename__ = "smms_failures"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_system: Mapped[str] = mapped_column(String(50), default="SMMS")
    railway_zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    division: Mapped[str | None] = mapped_column(String(100), nullable=True)
    section_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    route_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    signal_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    equipment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    failure_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    failure_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    overdue_hours: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    failure_started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requires_power_isolation: Mapped[bool | None] = mapped_column(Boolean, default=False)
    related_block_request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
