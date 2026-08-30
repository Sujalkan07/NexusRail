from sqlalchemy import Boolean, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TmsDefect(Base):
    __tablename__ = "tms_defects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_system: Mapped[str] = mapped_column(String(50), default="TMS")
    railway_zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    division: Mapped[str | None] = mapped_column(String(100), nullable=True)
    section_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    route_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    track_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    km_post: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    defect_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    defect_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_critical: Mapped[bool | None] = mapped_column(Boolean, default=False)
    priority_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    reported_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    detected_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_repair_hours: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    created_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
